from fastapi import Form, UploadFile, File, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
import json
from app.db.database import get_db
from app.db.crud.auth import require_roles
from app.db.crud.account import update_user_info
from app.db.schemas.request.account_request import user_update
from app.db.crud.collaborator import has_applied_as_collaborator, create_collaborator_application
from app.db.crud.project import get_project_by_id
from app.db.crud.project_idea import create_project_idea 
from app.db.schemas.request.project_idea_request import ProjectIdeaRequest   
    
router = APIRouter(prefix="/user", tags=["user"])

# ================= API: user-info =================
@router.get("/profile")
def get_user_profile(
    user=Depends(require_roles(["admin","staff","user"]))
):
    return {
        "account_id": user.id_account,
        "full_name": user.full_name,
        "email": user.email,
        "phone": user.phone,
    }
    
@router.patch("/update-profile")
def update_user_profile(
    data: user_update,
    db: Session = Depends(get_db),
    admin=Depends(require_roles(["user"]))
):
    if admin.role.name != "user":
        raise HTTPException(status_code=403, detail="Bạn không có quyền cập nhật thông tin user")
    updated = update_user_info(
        db,
        admin.id_account,
        full_name=data.full_name,
        phone=data.phone,
        password=data.password
    )
    if not updated:
        raise HTTPException(404, detail="Không tìm thấy tài khoản user")
    return {"message": "Cập nhật thông tin admin thành công"}

@router.post("/send-idea")
def send_idea(
    idea: ProjectIdeaRequest, 
    user=Depends(require_roles(["user"])),
    db: Session = Depends(get_db)
):
    # Kiểm tra dự án có tồn tại không
    project = get_project_by_id(db, idea.id_project)
    if not project:
        raise HTTPException(status_code=404, detail="Project không tồn tại")
    create_project_idea(db, user.id_account, idea.id_project, idea.description)
    return {"message": "Ủng hộ ý tưởng thành công!"} 

@router.post("/apply-collaborator")
def apply_collaborator(
    project_id: str = Form(...),
    user=Depends(require_roles(["user"])),
    db: Session = Depends(get_db)
):
    project = get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project không tồn tại")
    if has_applied_as_collaborator(db, user.id_account, project_id):
        raise HTTPException(status_code=400, detail="Bạn đã đăng ký làm cộng tác viên cho dự án này")
    create_collaborator_application(db, user.id_account, project_id)
    return {"message": "Đăng ký làm cộng tác viên thành công!"}