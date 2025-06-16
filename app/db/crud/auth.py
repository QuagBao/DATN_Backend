import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.models import Account
from app.db.database import get_db
from app.db.crud import account as account_crud
from app.utils.utils import verify_password
from app.db.crud.account import get_account_by_email
from jose import jwt, JWTError
from fastapi.security import APIKeyHeader

load_dotenv()

# Constants
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 120))

bearer_scheme = APIKeyHeader(name="Authorization", auto_error=True)


def get_current_user(token: str = Depends(bearer_scheme), db: Session = Depends(get_db)):
    # Nếu token có dạng "Bearer <token>" thì cắt bỏ phần "Bearer "
    if token.lower().startswith("bearer "):
        token = token[7:]
    try:
        # Giải mã token để lấy user_id từ payload
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token không hợp lệ")
        # Truy vấn user trong DB
        user = account_crud.get_account_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
        return user

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Token không hợp lệ",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
def require_roles(roles: list[str]):
    def role_checker(user: Account = Depends(get_current_user)):
        if user.role.name not in roles:
            raise HTTPException(status_code=403, detail="Permission denied")
        return user
    return role_checker

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def login_account(db, account):
    db_account = get_account_by_email(db, account.email)
    if db_account.status == "pending":
        raise HTTPException(status_code=403, detail="Tài khoản chưa được kích hoạt")
    if db_account.status == "blocked":
        raise HTTPException(status_code=403, detail="Tài khoản đã bị khóa")
    if db_account and verify_password(account.password, db_account.password):
        token = create_access_token(data={"sub": db_account.id_account})
        return db_account, token  # ✅ trả user và token
    return None, None

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # payload là dict, ví dụ: {"sub": "...", "exp": ...}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )