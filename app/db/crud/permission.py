from sqlalchemy.orm import Session
from app.db import models

def get_all_permissions(db: Session):
    """
    Lấy tất cả quyền từ cơ sở dữ liệu
    """
    return db.query(models.Permission).all()

