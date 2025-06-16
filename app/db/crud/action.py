from sqlalchemy.orm import Session
from app.db.models import action , permission

def get_all_actions(db: Session):
    """
    Lấy tất cả hành động từ cơ sở dữ liệu
    """
    return db.query(action).all()

def get_action_by_id(db: Session, id: str):
    """
    Lấy hành động theo id từ cơ sở dữ liệu
    """
    return db.query(action).filter(action.id_action == id).first()
    
def get_action_name_by_permission(db, permission_id):
    Permissions = db.query(permission).filter(permission.id_permission == permission_id).first()
    if not Permissions:
        return None

    Actions = db.query(action).filter(action.id_action == permission.id_action).first()
    if not Actions:
        return None

    return Actions.name
