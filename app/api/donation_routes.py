from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query,Response
from fastapi import APIRouter, UploadFile, File, Form
from sqlalchemy.orm import Session
import logging
# === Schemas ===
from app.db.schemas.request.donation_request import DonationCreate
# === Database & CRUD ===
from app.db import database
from app.db.crud import donation as crud_donation
from app.db.crud import project as crud_project
from app.db.crud import account as crud_account
from app.db.crud.auth import require_roles
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from app.utils.ws_manager import manager
import asyncio

router = APIRouter(prefix="/donation", tags=["donations"])
logger = logging.getLogger(__name__)

# ================= Donation =================
@router.post("/create")
async def create_donation(
    donation: DonationCreate,
    db: Session = Depends(database.get_db),
):
    # Nếu có account_id thì query tài khoản ra
    if donation.account_id:
        user = crud_account.get_account_by_id(db=db, id=donation.account_id)
        if not user:
            raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản")
        
        full_name = user.full_name
        email = user.email
        phone = user.phone
    else:
        # Dùng thông tin từ payload
        full_name = donation.full_name
        email = donation.email
        phone = donation.phone

    # Tạo donation
    user_donate = crud_donation.create_donation(
        db=db,
        donation_data=donation,
        id=donation.account_id if donation.account_id else None,
        full_name=full_name,
        email=email,
        phone=phone
    )
    # Cập nhật số tiền hiện tại của project
    current_numeric = crud_project.get_current_numeric_by_project(db=db, id_project=donation.project_id)
    current_numeric += donation.amount
    crud_project.update_current_numeric(db=db, id_project=donation.project_id, new_numeric=current_numeric)

    # Trả về
    return {
        "message": "Đã ủng hộ thành công",
        "name_project": user_donate.project.name_project
    }
