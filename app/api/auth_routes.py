from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query,Response
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List,Union
import logging
from random import randint
# === Ultils ===
from app.utils.send_email import send_register_otp_email, send_forgot_password_otp_email
from app.utils.redis_client import redis_client
from app.utils import utils
# === Schemas ===
from app.db.schemas.request.auth_request import OTPVerifyRequest, ForgotPasswordRequest, PasswordResetRequest, OTPResendRequest, PasswordChangeRequest
from app.db.schemas.request.account_request import account_create, account_login
from app.db.schemas.response.account_response import account_out
from app.db.schemas.response.login_response import LoginResponse
# === Database & CRUD ===
from app.db.crud import account as account_crud
from app.db.crud import auth as auth_crud
from app.db import database

router = APIRouter(prefix="", tags=["auth"])
logger = logging.getLogger(__name__)
        
# ================= API: auth =================

@router.post("/register")
def register_account(account: account_create, db: Session = Depends(database.get_db)):
    db_account = account_crud.get_account_by_email(db, account.email)
    if db_account:
        return {
            "message": "Email đã tồn tại trong hệ thống."
        }
    account_crud.create_account(db=db, account=account)
    otp = str(randint(10000, 99999))
    print("OTP gửi đi:", otp)
    result = redis_client.setex(f"otp:{account.email}", 300, otp)
    print("Đã lưu Redis:", result)
    send_register_otp_email(account.email, otp)
    return {
        "message": "Đã gửi mã xác thực đến email để kích hoạt tài khoản."
    }

@router.post("/register/resend-otp")
def resend_register_otp(email: OTPResendRequest):
    otp = str(randint(10000, 99999))
    redis_client.setex(f"otp:{email.email}", 300, otp)
    send_register_otp_email(email.email, otp)
    return {
        "message": "Mã OTP mới đã được gửi đến email của bạn."
    }


@router.post("/register/verify-otp")
def verify_otp(data: OTPVerifyRequest, db: Session = Depends(database.get_db)):
    saved_otp = redis_client.get(f"otp:{data.email}")
    if not saved_otp:
        return {
            "message": "Mã OTP đã hết hạn hoặc không tồn tại."
        }
    if data.otp != saved_otp:
        return {
            "message": "Mã OTP không chính xác."
        }
    account_crud.update_account_status(db, data.email, "active")
    # Xóa mã OTP sau khi xác thực thành công
    redis_client.delete(f"otp:{data.email}")
    return {
        "message": "Xác thực thành công. Tài khoản đã kích hoạt."
    }

@router.post("/login", response_model=LoginResponse)
def login(account: account_login, db: Session = Depends(database.get_db)):
    user, token = auth_crud.login_account(db, account)
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Sai email hoặc mật khẩu"
        )
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user 
    }

@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(database.get_db)):
    account = account_crud.get_account_by_email(db, data.email)
    if not account:
        return {
            "message": "Email không tồn tại."
        }
    otp = str(randint(10000, 99999))
    redis_client.setex(f"otp:{account.email}", 300, otp)
    send_forgot_password_otp_email(data.email, otp)
    return {
        "message": "OTP đã được gửi đến email của bạn."
    }

@router.post("/forgot-password/resend-otp")
def resend_forgot_password_otp(email: OTPResendRequest, db: Session = Depends(database.get_db)):
    account = account_crud.get_account_by_email(db, email.email)
    if not account:
        return {
            "message": "Email không tồn tại."
        }
    otp = str(randint(10000, 99999))
    redis_client.setex(f"otp:{email.email}", 300, otp)
    send_forgot_password_otp_email(email.email, otp)
    return {"message": "Mã OTP mới đã được gửi đến email của bạn."}


@router.post("/forgot-password/verify-otp-reset")
def verify_otp_reset(data: OTPVerifyRequest):
    saved_otp = redis_client.get(f"otp:{data.email}")
    if not saved_otp:
        return {
            "message": "Mã OTP đã hết hạn hoặc không tồn tại."
        }
    if saved_otp != data.otp:
        return {
            "message": "Mã OTP không chính xác."
        }
    return {"message": "OTP hợp lệ. Tiếp tục đặt lại mật khẩu."}

@router.post("/forgot-password/reset-password")
def reset_password(data: PasswordResetRequest, db: Session = Depends(database.get_db)):
    saved_otp = redis_client.get(f"otp:{data.email}")
    if not saved_otp:
        return {
            "message": "Mã OTP đã hết hạn hoặc không tồn tại."
        }
    if data.otp != saved_otp:
        return {
            "message": "Mã OTP không chính xác."
        }
    account = account_crud.get_account_by_email(db, data.email)
    if not account:
        return {
            "message": "Tài khoản không tồn tại."
        }
    account_crud.update_password_by_email(db, data.email, data.new_password)
    redis_client.delete(f"otp:{data.email}")
    return {"message": "Đặt lại mật khẩu thành công."}

@router.post("/change-password")
def change_password(data: PasswordChangeRequest, db: Session = Depends(database.get_db)):
    # 1. Giải mã token
    try:
        payload = auth_crud.decode_access_token(data.token)
        id_account = payload.get("sub")
        if id_account is None:
            raise HTTPException(status_code=401, detail="Token không hợp lệ.")
    except Exception:
        raise HTTPException(status_code=401, detail="Token không hợp lệ.")
    # 2. Tìm account theo ID
    account = account_crud.get_account_by_id(db, id_account)
    if not account:
        raise HTTPException(status_code=404, detail="Tài khoản không tồn tại.")
    # 3. Kiểm tra mật khẩu cũ
    if data.new_password == data.old_password:
        raise HTTPException(status_code=400, detail="Mật khẩu mới không được trùng mật khẩu cũ.")
    if not utils.verify_password(data.old_password, account.password):
        raise HTTPException(status_code=400, detail="Mật khẩu cũ không chính xác.")
    # 4. Cập nhật mật khẩu mới
    account_crud.update_password_by_id(db, account.id_account, data.new_password)
    return {"message": "Đổi mật khẩu thành công."}

