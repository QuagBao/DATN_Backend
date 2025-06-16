from sqlalchemy.orm import Session
from app.db import models
from app.db.schemas.request.account_request import account_create
from app.utils.utils import hash_password

def create_account(db: Session, account: account_create):
    db_account = models.Account(
        email=account.email,
        password=hash_password(account.password),  # ✅ khớp với __init__
        phone=account.phone,
        full_name=account.full_name,
        status="pending",  # hoặc None nếu không cần
        id_role=1  # role mặc định
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)

def get_account_by_email(db: Session, email: str):
    return db.query(models.Account).filter(models.Account.email == email).first()

def get_account_by_id(db: Session, id: str):  # UUID string
    return db.query(models.Account).filter(models.Account.id_account == id).first()

def update_account_status(db: Session, email: str, new_status: str):
    account = get_account_by_email(db, email)
    account.status = new_status
    db.commit()
    return account

def update_password_by_email(db: Session, email: str, new_password: str):
    account = get_account_by_email(db, email)
    account.password = hash_password(new_password)
    db.commit()
    db.refresh(account)
    return account

def update_password_by_id(db: Session, id: str, new_password: str):
    account = get_account_by_id(db, id)
    account.password = hash_password(new_password)
    db.commit()
    db.refresh(account)
    return account

def update_admin_info(db: Session, admin_id, full_name=None, phone=None, password=None):
    admin = db.query(models.Account).filter(models.Account.id_account == admin_id).first()
    if not admin:
        return None
    if full_name:
        admin.full_name = full_name
    if phone:
        admin.phone = phone
    if password:
        admin.password = hash_password(password)
    db.commit()
    db.refresh(admin)
    return admin

def update_staff_info(db: Session, staff_id, full_name=None, phone=None, password=None):
    staff = db.query(models.Account).filter(models.Account.id_account == staff_id).first()
    if not staff:
        return None
    if full_name:
        staff.full_name = full_name
    if phone:
        staff.phone = phone
    if password:
        staff.password = hash_password(password)
    db.commit()
    db.refresh(staff)
    return staff
    
def update_user_info(db: Session, staff_id, full_name=None, phone=None, password=None):
    staff = db.query(models.Account).filter(models.Account.id_account == staff_id).first()
    if not staff:
        return None
    if full_name:
        staff.full_name = full_name
    if phone:
        staff.phone = phone
    if password:
        staff.password = hash_password(password)
    db.commit()
    db.refresh(staff)
    return staff