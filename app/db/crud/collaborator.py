# app/db/crud/project_collaborator.p
from sqlalchemy.orm import Session
from app.db.models.project_collaborator import ProjectCollaborator
from datetime import datetime, time, timedelta
from sqlalchemy.orm import joinedload
from app.db.models.account import Account
from app.db.models.project import Project
from sqlalchemy import or_
from typing import Optional
from app.db.models.project_collaborator import ProjectCollaborator

def has_applied_as_collaborator(db: Session, account_id: str, project_id: str) -> bool:
    return db.query(ProjectCollaborator).filter_by(
        account_id=account_id,
        project_id=project_id
    ).first() is not None

def create_collaborator_application(db: Session, account_id: str, project_id: str):
    new_collaborator = ProjectCollaborator(
        account_id=account_id,
        project_id=project_id,
        status= "pending",  # pending
        applied_at=datetime.utcnow()
    )
    db.add(new_collaborator)
    db.commit()

def get_all_collaborator(
    db: Session,
    skip=0,
    limit=40,
    name_project: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None,
    universal_search: Optional[str] = None
):
    query = db.query(ProjectCollaborator).options(
        joinedload(ProjectCollaborator.account),
        joinedload(ProjectCollaborator.project)
    ).join(ProjectCollaborator.account).join(ProjectCollaborator.project)
    
    if name_project:
        query = query.filter(Project.name_project.ilike(f"%{name_project}%"))
    if status:
        query = query.filter(ProjectCollaborator.status == status)
    
    if start_date and end_date:
        end_datetime = datetime.combine(end_date, time(23, 59, 59))
        start_datetime = datetime.combine(start_date, time(0, 0, 0))
        query = query.filter(ProjectCollaborator.applied_at >= start_datetime, ProjectCollaborator.applied_at <= end_datetime)
    elif start_date:
        start_datetime = datetime.combine(start_date, time(0, 0, 0))
        query = query.filter(ProjectCollaborator.applied_at >= start_datetime)
    elif end_date:
        end_datetime = datetime.combine(end_date, time(23, 59, 59))
        query = query.filter(ProjectCollaborator.applied_at <= end_datetime)
    
    if universal_search:
        query = query.filter(
            or_(
                Account.full_name.ilike(f"%{universal_search}%"),
                Account.email.ilike(f"%{universal_search}%"),
                Account.phone.ilike(f"%{universal_search}%")
            )
        )
    total = query.count()
    collaborators = query.offset(skip).limit(limit).all()
    return collaborators, total

def get_all_collaborator_approved(
    db: Session,
    skip=0,
    limit=40,
    name_project: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None,
    universal_search: Optional[str] = None
):
    query = db.query(ProjectCollaborator).options(
        joinedload(ProjectCollaborator.account),
        joinedload(ProjectCollaborator.project)
    ).join(ProjectCollaborator.account).join(ProjectCollaborator.project)
    
    if name_project:
        query = query.filter(Project.name_project.ilike(f"%{name_project}%"))
    if status:
        query = query.filter(ProjectCollaborator.status == status)
    
    if start_date and end_date:
        end_datetime = datetime.combine(end_date, time(23, 59, 59))
        start_datetime = datetime.combine(start_date, time(0, 0, 0))
        query = query.filter(ProjectCollaborator.approved_at >= start_datetime, ProjectCollaborator.approved_at <= end_datetime)
    elif start_date:
        start_datetime = datetime.combine(start_date, time(0, 0, 0))
        query = query.filter(ProjectCollaborator.approved_at >= start_datetime)
    elif end_date:
        end_datetime = datetime.combine(end_date, time(23, 59, 59))
        query = query.filter(ProjectCollaborator.approved_at <= end_datetime)
    
    if universal_search:
        query = query.filter(
            or_(
                Account.full_name.ilike(f"%{universal_search}%"),
            )
        )
    total = query.count()
    collaborators = query.offset(skip).limit(limit).all()
    return collaborators, total


def get_collaborator_by_id(db: Session, id: str):
    return db.query(ProjectCollaborator).filter_by(id=id).first()

def update_status_collaborator(db: Session, id: str):
    collaborator = db.query(ProjectCollaborator).filter_by(id=id).first()
    if collaborator:
        collaborator.status = "active"
        collaborator.approved_at = datetime.utcnow() + timedelta(hours=7)
        db.commit()
        return True
    return False

def delete_collaborator_by_id(db: Session, id_collaborator: str) -> bool:
    collaborator = db.query(ProjectCollaborator).filter_by(id=id_collaborator).first()
    if not collaborator:
        return False
    db.delete(collaborator)
    db.commit()
    return True

def get_collaborator_by_project_id(db: Session, project_id: str):
    collaborators = (
        db.query(ProjectCollaborator)
        .filter_by(project_id=project_id)
        .options(
            joinedload(ProjectCollaborator.account),   # load bảng Account
            joinedload(ProjectCollaborator.project)    # load bảng Project
        )
        .all()
    )
    return collaborators