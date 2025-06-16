from sqlalchemy.orm import Session
from app.db.models import resource,permission

def get_all_resources(db: Session):
    """
    Lấy tất cả tài nguyên từ cơ sở dữ liệu
    """
    return db.query(resource).all()
    
def get_resource_by_id(db: Session, id: str):
    """
    Lấy tài nguyên theo id từ cơ sở dữ liệu
    """
    return db.query(resource).filter(resource.id_resource == id).first()
    
def get_resource_name_by_permission(db, permission_id):
    Permission = db.query(permission).filter(permission.id_permission == permission_id).first()
    if not Permission:
        return None

    Resources = db.query(resource).filter(resource.id_resource == permission.id_resource).first()
    if not Resources:
        return None

    return Resources.name
