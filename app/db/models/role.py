from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from app.db.database import Base

class Role(Base):
    __tablename__ = "roles"

    id_role = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    priority = Column(Integer, nullable=False, default=0)

    # Relationships
    accounts = relationship("Account", back_populates="role")
    role_permissions = relationship("RolePermissions", back_populates="role")  # ✅ qua bảng trung gian ORM

    def __init__(self, name, priority=0):
        self.name = name
        self.priority = priority

    def __repr__(self):
        return f"<Role(id='{self.id_role}', name='{self.name}', priority={self.priority})>"

    # Getters
    def get_name(self):
        return self.name

    def get_priority(self):
        return self.priority

    # Setters
    def set_name(self, new_name):
        self.name = new_name

    def set_priority(self, new_priority):
        self.priority = new_priority
