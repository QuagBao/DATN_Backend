# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()  # Load biến môi trường từ .env

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL chưa được cấu hình trong .env")
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={
        "ssl": {"ssl": True},
        "charset": "utf8mb4"
    }
)

# Kiểm tra kết nối
try:
    with engine.connect() as conn:
        print("✅ Kết nối đến MySQL thành công!")
except Exception as e:
    print(f"❌ Lỗi kết nối MySQL: {e}")
    
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
