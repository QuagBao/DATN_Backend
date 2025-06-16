import os
import sys
import uvicorn  # ✅ Bổ sung dòng này
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth_routes
from app.api import admin_routes
from app.api import project_routes
from app.api import user_routes
from app.api import staff_routes
from app.api import donation_routes
from app.db import models
from app.db.database import engine, SessionLocal
from app.seeder.seed_roles import seed_roles   # ✅ Import đúng hàm, không import nguyên module
from app.seeder.seed_admin import seed_admin_account  # ✅ Import đúng hàm, không import nguyên module
from app.seeder.seed_action import seed_actions  # ✅ Import đúng hàm, không import nguyên module
from fastapi.staticfiles import StaticFiles

# Thêm thư mục cha để import được module app.*
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Khởi tạo FastAPI application
app = FastAPI()

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sự kiện khi ứng dụng khởi động
@app.on_event("startup")
def on_startup():
    print("✅ Kết nối đến MySQL thành công!")
    models.Base.metadata.create_all(bind=engine)  # Tạo bảng nếu chưa tồn tại
    db = SessionLocal()
    seed_roles(db)
    seed_admin_account(db)# Seed 3 role mặc định
    seed_actions(db)
    db.close()

# Đăng ký router cho toàn bộ API
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(auth_routes.router)
app.include_router(admin_routes.router)
app.include_router(project_routes.router)
app.include_router(staff_routes.router)
app.include_router(donation_routes.router)
app.include_router(user_routes.router)