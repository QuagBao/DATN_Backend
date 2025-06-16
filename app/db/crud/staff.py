# app/db/crud/project.py
from app.db.models import Account
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime
from typing import Optional
from app.utils.utils import hash_password

def create_staff(db: Session, email):
    db_account = Account(
        email= email,
        password= hash_password("Password123@"),  # ✅ khớp với __init__
        phone="XXXXXXXXXX",
        full_name= "Clone",
        status="active",  # hoặc None nếu không cần
        id_role=2  # role mặc định
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    
def delete_staff(db: Session, id_staff: str):
    staff = db.query(Account).filter(Account.id_account == id_staff).first()
    if not staff:
        return None
    db.delete(staff)
    db.commit()
    return staff

def get_staff_by_id(db: Session, id: str):  # UUID string
    return db.query(Account).filter(Account.id_role == 2).filter(Account.id_account == id).first()

def get_all_staff(
    db: Session,
    skip: int = 0,
    limit: int = 40,
    universal_search: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    status: Optional[str] = None
):
    query = db.query(Account).filter(Account.id_role == 2)  # role staff
    if universal_search:
        query = query.filter(
            or_(
                Account.full_name.ilike(f"%{universal_search}%"),
                Account.email.ilike(f"%{universal_search}%"),
                Account.phone.ilike(f"%{universal_search}%")
            )
        )
    if start_date and end_date:
        query = query.filter(Account.created_at >= start_date, Account.created_at <= end_date)
    elif start_date:
        query = query.filter(Account.created_at >= start_date)
    elif end_date:
        query = query.filter(Account.created_at <= end_date)
    if status:
        query = query.filter(Account.status == status)
    total = query.count()
    staff_list = query.offset(skip).limit(limit).all()
    return staff_list, total


def get_all_users(
    db: Session,
    skip: int = 0,
    limit: int = 40,
    universal_search: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    status: Optional[str] = None
):
    query = db.query(Account).filter(Account.id_role == 1)  # Người dùng thường
    if universal_search:
        query = query.filter(
            or_(
                Account.full_name.ilike(f"%{universal_search}%"),
                Account.email.ilike(f"%{universal_search}%"),
                Account.phone.ilike(f"%{universal_search}%")
            )
        )
    if start_date and end_date:
        query = query.filter(Account.created_at >= start_date, Account.created_at <= end_date)
    elif start_date:
        query = query.filter(Account.created_at >= start_date)
    elif end_date:
        query = query.filter(Account.created_at <= end_date)
    if status:
        query = query.filter(Account.status == status)
    total = query.count()
    users = query.offset(skip).limit(limit).all()
    return users, total
