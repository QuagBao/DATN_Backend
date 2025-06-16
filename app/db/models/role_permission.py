from sqlalchemy import Column, String, Integer, ForeignKey
from app.db.database import Base
from sqlalchemy.orm import relationship

class RolePermissions(Base):
    __tablename__ = "role_permissions"

    id_role = Column(Integer, ForeignKey("roles.id_role"), primary_key=True)
    id_permission = Column(String(36), ForeignKey("permissions.id_permission"), primary_key=True)

    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission", back_populates="role_permissions")
