from fastapi import Form, UploadFile, File, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
import json
from app.db.database import get_db
from app.db.crud.auth import require_roles
from app.db.crud.account import update_user_info
from app.db.schemas.request.account_request import user_update
from app.db.crud.collaborator import create_collaborator_application
from app.db.crud.project import get_project_by_id
from app.db.crud.project_idea import create_project_idea 
from app.db.crud.account import get_account_by_id
from app.db.schemas.request.project_idea_request import ProjectIdeaRequest
from app.db.schemas.request.collaborator_request import CollaboratorRequest
    
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
    collaborator: CollaboratorRequest,
    db: Session = Depends(get_db)
):
    # 1. Kiểm tra project có tồn tại không
    project = get_project_by_id(db, collaborator.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project không tồn tại")

    # 2. Nếu có account_id → lấy user từ DB
    if collaborator.account_id:
        user = get_account_by_id(db, collaborator.account_id)
        if not user:
            raise HTTPException(status_code=404, detail="Account không tồn tại")
        
        # Gọi hàm tạo collaborator với thông tin user
        create_collaborator_application(
            db=db,
            project_id=collaborator.project_id,
            account_id=collaborator.account_id,
            full_name=user.full_name,
            email=user.email,
            phone=user.phone
        )
    else:
        # Không có account_id → dùng thông tin từ body
        if not collaborator.full_name or not collaborator.email or not collaborator.phone:
            raise HTTPException(status_code=400, detail="Thiếu thông tin liên hệ (full_name, email, phone)")
        create_collaborator_application(
            db=db,
            project_id=collaborator.project_id,
            full_name=collaborator.full_name,
            email=collaborator.email,
            phone=collaborator.phone
            # account_id=None mặc định
        )
    return {"message": "Đăng ký làm cộng tác viên thành công!"}
