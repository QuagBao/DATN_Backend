from fastapi import Form, UploadFile, File, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
import json
from app.db.schemas.request.account_request import staff_update
from pathlib import Path
from datetime import datetime
from random import randint
# === Ultils ===
from app.utils.send_email import send_register_otp_email, send_forgot_password_otp_email
from app.utils.redis_client import redis_client
from app.db.crud.account import get_account_by_id
from app.db.database import get_db
from app.db.crud.auth import require_roles
from app.db.crud.account import update_staff_info
from app.db.crud.project import (
    update_project,
    delete_project,
    get_projects_by_owner,
    get_project_by_owner_and_name
)
from app.db.schemas.request.project_request import project_create, project_update

router = APIRouter(prefix="/staff", tags=["staff"])

# ================= API: staff-info =================
@router.patch("/update-profile")
def update_staff_profile(
    data: staff_update,
    db: Session = Depends(get_db),
    staff=Depends(require_roles(["staff"]))
):
    staff_account = get_account_by_id(db, staff.id_account)
    if not staff_account:
        raise HTTPException(404, "Không tìm thấy tài khoản staff")
    if staff_account.role.name != "staff":
        raise HTTPException(403, "Bạn không có quyền cập nhật thông tin nhân viên")
    updated = update_staff_info(
        db,
        staff.id_account,
        full_name=data.full_name,
        phone=data.phone,
        password=data.password
    )
    if not updated:
        raise HTTPException(404, detail="Không tìm thấy tài khoản staff")
    return {"message": "Cập nhật thông tin nhân viên thành công"}

# ================= API: project =================
@router.patch("/projects/update-by-owner")
def update_project_by_name_endpoint(
    name_project: str = Form(...),
    data: str = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    staff=Depends(require_roles(["staff"]))
):
    try:
        parsed_data = project_update(**json.loads(data))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Dữ liệu JSON không hợp lệ")
    if staff.role.name != "staff":
        raise HTTPException(status_code=403, detail="Bạn không có quyền cập nhật dự án")
    project = get_project_by_owner_and_name(db, staff.id_account, name_project)
    if not project:
        raise HTTPException(status_code=404, detail="Không tìm thấy dự án theo tên và chủ sở hữu")

    updated_project = update_project(db, project.id_project, parsed_data, image)
    return {"message": "Cập nhật dự án thành công", "id_project": updated_project.id_project}

@router.delete("/projects/delete-by-owner")
def delete_project_by_name_endpoint(
    name_project: str = Form(...),
    db: Session = Depends(get_db),
    staff=Depends(require_roles(["staff"]))
):
    if staff.role.name != "staff":
        raise HTTPException(status_code=403, detail="Bạn không có quyền xóa dự án")
    project = get_project_by_owner_and_name(db, staff.id_account, name_project)
    if not project:
        raise HTTPException(status_code=404, detail="Không tìm thấy dự án")
    delete_project(db, project.id_project)
    return {"message": "Xóa dự án thành công", "id_project": project.id_project}

@router.get("/projects/by-owner")
def get_projects_by_owner_endpoint(
    skip: int = 0,
    limit: int = 40,
    db: Session = Depends(get_db),
    staff = Depends(require_roles(["staff"]))
):
    if staff.role.name != "staff":
        raise HTTPException(status_code=403, detail="Bạn không có quyền xem dự án của người dùng khác")
    projects, total = get_projects_by_owner(db, staff.id_account, skip=skip, limit=limit)
    return {
        "total": total,
        "data": projects,
        "skip": skip,
        "limit": limit
    }