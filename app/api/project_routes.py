from fastapi import Form, UploadFile, File, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
import json
from typing import Optional, List
from datetime import date , datetime
from app.db.schemas.request.project_request import project_create, project_update
from app.db.crud.project import create_project , get_total_collaborators_and_donors_by_project, get_all_projects
from app.db.database import get_db
from app.db.crud.auth import require_roles
from app.db.crud.project import get_total_collaborators_and_donors, get_projects_in_progress, get_project_by_id
from app.db.schemas.response.project_response import ProjectOut, ProjectWithStats
from app.db.schemas.response.paginated_response import PaginatedResponse  # nếu có
from app.db.crud.donation import get_all_donations
from app.db.crud.collaborator import get_all_collaborator, get_all_collaborator_approved
from math import ceil
from app.model_AI.content_summarization_processor import (
    summarize_text,
    load_model_and_tokenizer
)
from app.db.crud.project import delete_project, get_project_by_owner_and_name, delete_image_by_id_project

router = APIRouter(prefix="", tags=["project"])

#================== API: project =================
@router.get("/projects/in-progress", response_model=PaginatedResponse[ProjectWithStats])
def get_projects_in_progress_endpoint(
    page: int = 1,
    limit: int = 40,
    db: Session = Depends(get_db)
):
    if page < 1:
        raise HTTPException(status_code=400, detail="Page phải lớn hơn 0")
    skip = (page - 1) * limit
    projects, total = get_projects_in_progress(db, skip=skip, limit=limit)
    total_pages = ceil(total / limit)
    # Tính collaborator và donor cho từng project
    result = []
    for project in projects:
        total_col, total_don = get_total_collaborators_and_donors_by_project(db, project.id_project)
        result.append(ProjectWithStats(
            **ProjectOut.model_validate(project).model_dump(),
            total_collaborators=total_col,
            total_donors=total_don
        ))
    return {
        "page": page,
        "limit": limit,
        "total_items": total,
        "total_pages": total_pages,
        "data": result
    }

@router.get("/dashboard/summary")
def get_system_summary(db: Session = Depends(get_db)):
    return get_total_collaborators_and_donors(db)

@router.get("/projects/{id_project}", response_model=ProjectWithStats)
def get_project_by_id_endpoint(id_project: str, db: Session = Depends(get_db)):
    project = get_project_by_id(db, id_project)
    if not project:
        raise HTTPException(status_code=404, detail="Project không tồn tại")

    total_col, total_don = get_total_collaborators_and_donors_by_project(db, id_project)
    return ProjectWithStats(
        **ProjectOut.model_validate(project).model_dump(),
        total_collaborators=total_col,
        total_donors=total_don
    )

@router.get("/projects", response_model=PaginatedResponse[ProjectWithStats])
def get_all_projects_endpoint(
    page: int = 1,
    limit: int = 40,
    name_project: Optional[str] = None,   
    start_date: Optional[date] = None, 
    end_date: Optional[date] = None,    
    status: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    if page < 1:
        raise HTTPException(status_code=400, detail="Page phải lớn hơn 0")
    skip = (page - 1) * limit
    projects, total = get_all_projects(
        db, skip=skip, limit=limit,
        name_project = name_project,
        start_date=start_date,
        end_date=end_date,
        status=status
    )
    total_pages = ceil(total / limit)
    result = []
    for project in projects:
        total_col, total_don = get_total_collaborators_and_donors_by_project(db, project.id_project)
        result.append(ProjectWithStats(
            **ProjectOut.model_validate(project).model_dump(),
            total_collaborators=total_col,
            total_donors=total_don
        ))
    return {
        "page": page,
        "limit": limit,
        "total_items": total,
        "total_pages": total_pages,
        "data": result
    }

# ================= LOAD NLP MODEL: SUMMARIZATION =================
summary_model, summary_tokenizer = load_model_and_tokenizer()
# ================= API: project =================
@router.post("/projects/create")
def create_project_endpoint(
    data: str = Form(...),
    images: List[UploadFile] = File(...),  # Danh sách ảnh
    db: Session = Depends(get_db),
    user = Depends(require_roles(["staff", "admin"]))
):
    try:
        parsed_data = project_create(**json.loads(data))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Dữ liệu JSON không hợp lệ")
    if user.role.name not in ["staff", "admin"]:
        raise HTTPException(status_code=403, detail="Bạn không có quyền tạo dự án")
    if not parsed_data.content.strip():
        raise HTTPException(status_code=400, detail="Missing or empty 'content' field")
    summary = summarize_text(
        text=parsed_data.content,
        model=summary_model,
        tokenizer=summary_tokenizer,
        max_length= 512,
        summary_max_length= 200,
        num_beams= 5
    )
    create_project(db, parsed_data,summary, images, user.id_account)
    return {"message": "Tạo dự án thành công"}

@router.delete("/projects/delete-by-owner")
def delete_project_by_name_endpoint(
    name_project: str = Form(...),
    db: Session = Depends(get_db),
    user =Depends(require_roles(["admin,staff"]))
):
    if user.role.name != "staff" or user.role.name != "admin":
        raise HTTPException(status_code=403, detail="Bạn không có quyền xóa dự án")
    project = get_project_by_owner_and_name(db, user.id_account, name_project)
    if not project:
        raise HTTPException(status_code=404, detail="Không tìm thấy dự án")
    delete_project(db, project.id_project)
    delete_image_by_id_project(db, project.id_project)
    return {"message": "Xóa dự án thành công", "id_project": project.id_project}

#================= API: Donations =================
@router.get("/donations")
def get_all_donations_endpoint(
    page: int = 1,
    limit: int = 40,
    account_name: Optional[str] = None,
    project_name: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
):
    # Parse ngày
    start = None
    end = None
    try:
        if start_date:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
        if end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="start_date/end_date phải đúng định dạng YYYY-MM-DD")
    skip = (page - 1) * limit
    donations, total = get_all_donations(
        db,
        skip=skip,
        limit=limit,
        account_name=account_name,
        project_name=project_name,
        start_date=start,
        end_date=end
    )
    total_pages = ceil(total / limit) if total > 0 else 1
    result = []
    for donation in donations:
        result.append({
            "id_donation": donation.id,
            "account_name": donation.account.full_name,
            "project_name": donation.project.name_project,
            "amount": donation.amount,
            "paytime": donation.paytime,
            "transaction_id": donation.transaction_id
        })
    return {
        "page": page,
        "limit": limit,
        "total_items": total,
        "total_pages": total_pages,
        "data": result
    }
    
# ================= API: collaborator =================
@router.get("/collaborators")
def get_all_collaborators_endpoint(
    page: int = 1,
    limit: int = 40,
    name_project: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    universal_search: Optional[str] = None,
    db: Session = Depends(get_db),
):   
    # Parse ngày
    start = None
    end = None
    try:
        if start_date:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
        if end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="start_date/end_date phải đúng định dạng YYYY-MM-DD")
    skip = (page - 1) * limit
    collaborators, total = get_all_collaborator(
        db,
        skip=skip,
        limit=limit,
        name_project=name_project,
        status=status,
        start_date=start,
        end_date=end,
        universal_search=universal_search
    )
    total_pages = ceil(total / limit) if total > 0 else 1
    result = []
    for collaborator in collaborators:
        result.append({
            "id_collaborator": collaborator.id,
            "account_name": collaborator.account.full_name,
            "email": collaborator.account.email,
            "phone": collaborator.account.phone,
            "project_name": collaborator.project.name_project,
            "status": collaborator.status,
            "applied_at": collaborator.applied_at,
            "approved_at": collaborator.approved_at
        })
    
    return {
        "page": page,
        "limit": limit,
        "total_items": total,
        "total_pages": total_pages,
        "data": result
    }
    
@router.get("/active-collaborators")
def get_active_collaborators_endpoint(
    page: int = 1,
    limit: int = 40,
    name_project: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    universal_search: Optional[str] = None,
    db: Session = Depends(get_db),
):   
    # Parse ngày
    start = None
    end = None
    try:
        if start_date:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
        if end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="start_date/end_date phải đúng định dạng YYYY-MM-DD")
    skip = (page - 1) * limit
    # status được set cố định "active"
    collaborators, total = get_all_collaborator_approved(
        db,
        skip=skip,
        limit=limit,
        name_project=name_project,
        status="active",
        start_date=start,
        end_date=end,
        universal_search=universal_search
    )
    total_pages = ceil(total / limit) if total > 0 else 1
    result = []
    for collaborator in collaborators:
        result.append({
            "id_collaborator": collaborator.id,
            "account_name": collaborator.account.full_name,
            "email": collaborator.account.email,
            "phone": collaborator.account.phone,
            "project_name": collaborator.project.name_project,
            "status": collaborator.status,
            "applied_at": collaborator.applied_at,
            "approved_at": collaborator.approved_at
        })
    
    return {
        "page": page,
        "limit": limit,
        "total_items": total,
        "total_pages": total_pages,
        "data": result
    }
