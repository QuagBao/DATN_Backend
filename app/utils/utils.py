from passlib.context import CryptContext

# Cấu hình mã hóa mật khẩu
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hàm để hash mật khẩu
def hash_password(password: str):
    return pwd_context.hash(password)

# Hàm để so sánh mật khẩu
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
