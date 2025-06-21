from sqlalchemy.orm import Session
from app.db.models import Donation, Account, Project
from app.db.schemas.request.donation_request import DonationCreate
from sqlalchemy.orm import joinedload
from sqlalchemy import or_
from typing import Optional
from datetime import datetime, date, time

def create_donation(
    db: Session,
    donation_data: DonationCreate,
    id: Optional[str],
    full_name: Optional[str],
    email: Optional[str],
    phone: Optional[str]
) -> Donation:
    new_donation = Donation(
        account_id=id,
        full_name=full_name,
        email=email,
        phone=phone,
        project_id=donation_data.project_id,
        amount=donation_data.amount,
        paytime=donation_data.paytime,
        transaction_id=donation_data.transaction_id
    )
    db.add(new_donation)
    db.commit()
    db.refresh(new_donation)
    return new_donation



def get_donation_by_project_id(db: Session, project_id: str):
    donors = (
        db.query(Donation)
        .filter_by(project_id=project_id)
        .options(
            joinedload(Donation.project)    # load bảng Project
        )
        .all()
    )
    return donors


def get_all_donations(
    db: Session,
    skip: int = 0,
    limit: int = 40,
    account_name: Optional[str] = None,
    project_name: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    query = db.query(Donation).options(
        joinedload(Donation.project)
    ).join(Donation.project)

    # Lọc theo account_name lưu trong Donation (không còn join Account)
    if account_name:
        query = query.filter(Donation.full_name.ilike(f"%{account_name}%"))
    
    # Lọc theo project_name
    if project_name:
        query = query.filter(Project.name_project.ilike(f"%{project_name}%"))

    # Lọc theo ngày
    if start_date and end_date:
        end_datetime = datetime.combine(end_date, time(23, 59, 59))
        start_datetime = datetime.combine(start_date, time(0, 0, 0))
        query = query.filter(Donation.paytime >= start_datetime, Donation.paytime <= end_datetime)
    elif start_date:
        start_datetime = datetime.combine(start_date, time(0, 0, 0))
        query = query.filter(Donation.paytime >= start_datetime)
    elif end_date:
        end_datetime = datetime.combine(end_date, time(23, 59, 59))
        query = query.filter(Donation.paytime <= end_datetime)

    # Tổng số record
    total = query.count()

    # Paging
    donations = query.offset(skip).limit(limit).all()
    return donations, total
