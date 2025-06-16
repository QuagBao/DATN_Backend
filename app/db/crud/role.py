from sqlalchemy.orm import Session
from app.db.models import Role, RolePermissions

def get_role_by_name(role_name: str, db: Session):
    """
    Lấy thông tin role theo tên
    """
    return db.query(Role).filter(Role.name == role_name).first()
    
def get_permission_ids_by_role_id(db, role_id):
    role_perms = db.query(RolePermissions).filter_by(id_role=role_id).all()
    return [rp.id_permission for rp in role_perms]

def set_permissions_for_role_id(db, role_id, permission_ids):
    # Xóa quyền cũ
    db.query(RolePermissions).filter(RolePermissions.id_role == role_id).delete()

    # Thêm quyền mới
    for perm_id in permission_ids:
        db.add(RolePermissions(id_role=role_id, id_permission=perm_id))

    db.commit()
