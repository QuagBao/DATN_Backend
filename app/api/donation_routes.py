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
from app.db.crud.auth import require_roles
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from app.utils.ws_manager import manager
import asyncio

router = APIRouter(prefix="/donation", tags=["donations"])
logger = logging.getLogger(__name__)

# ================= WebSocket =================
@router.websocket("/ws/project/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    await manager.connect(websocket, project_id)
    try:
        while True:
            await websocket.receive_text()  # giữ kết nối
    except WebSocketDisconnect:
        manager.disconnect(websocket, project_id)

# ================= Donation =================
@router.post("/create")
async def create_donation(
    donation: DonationCreate,
    db: Session = Depends(database.get_db),
    user = Depends(require_roles(["user"]))
):
    if user.role.name != "user":
        raise HTTPException(status_code=403, detail="Bạn không có quyền truy cập vào API này")
    user_donate = crud_donation.create_donation(db=db, donation_data=donation, id=user.id_account)
    current_numeric = crud_project.get_current_numeric_by_project(db=db, id_project=donation.project_id)
    current_numeric += donation.amount
    crud_project.update_current_numeric(db=db, id_project=donation.project_id, new_numeric=current_numeric)
    # 3. Gửi dữ liệu WebSocket (không block API)
    asyncio.create_task(
        manager.broadcast(
            project_id=donation.project_id,
            message={
                "project_id": donation.project_id,
                "current_numeric": current_numeric
            }
        )
    )
    # 4. Trả về thông báo
    return {
        "message": "Đã ủng hộ thành công",
        "name_project": user_donate.project.name_project
    }