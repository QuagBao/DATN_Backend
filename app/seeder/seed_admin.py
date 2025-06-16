import os
from sqlalchemy.orm import Session
from app.db.models.account import Account
from app.db.models.role import Role
from app.utils.utils import hash_password  # hoặc bất kỳ thư viện hash nào bạn dùng

def seed_admin_account(db: Session):
    admin_email = os.getenv("ADMIN_EMAIL", "admin@bkfund.vn")
    admin_password = os.getenv("ADMIN_PASSWORD", "Admin123@")
    admin_phone = os.getenv("ADMIN_PHONE", "0123456789")

    # 1. Kiểm tra tài khoản đã tồn tại chưa
    existing_admin = db.query(Account).filter_by(email=admin_email).first()
    if existing_admin:
        print("ℹ️ Admin account already exists.")
        return

    # 3. Tạo admin account
    admin_account = Account(
        email=admin_email,
        password=hash_password(admin_password),
        full_name="Super Admin",
        phone=admin_phone,
        status="active",
        id_role=3
    )

    db.add(admin_account)
    db.commit()
    print("✅ Admin account seeded.")
