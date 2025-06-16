import uuid
from sqlalchemy import Column, TIMESTAMP, ForeignKey
from sqlalchemy import String, Integer
from sqlalchemy.orm import relationship
from app.db.database import Base
class Permission(Base):
    __tablename__ = "permissions"

    id_permission = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    id_action = Column(Integer , ForeignKey("actions.id_action"))
    id_resource = Column(String(36), ForeignKey("resources.id_resource"))
    created_at = Column(TIMESTAMP, nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)
    deleted_at = Column(TIMESTAMP, nullable=True)

    # Relationships
    action = relationship("Action", back_populates="permissions")
    resource = relationship("Resource", back_populates="permissions")
    role_permissions = relationship("RolePermissions", back_populates="permission")

    def __init__(self, id_action, id_resource, created_at=None, updated_at=None, deleted_at=None):
        self.id_action = id_action
        self.id_resource = id_resource
        self.created_at = created_at
        self.updated_at = updated_at
        self.deleted_at = deleted_at

    def __repr__(self):
        return f"<Permission(id='{self.id_permission}', action='{self.id_action}', resource='{self.id_resource}')>"

    # Getters
    def get_id_action(self):
        return self.id_action

    def get_id_resource(self):
        return self.id_resource

    def get_created_at(self):
        return self.created_at

    def get_updated_at(self):
        return self.updated_at

    def get_deleted_at(self):
        return self.deleted_at

    # Setters
    def set_id_action(self, new_id_action):
        self.id_action = new_id_action

    def set_id_resource(self, new_id_resource):
        self.id_resource = new_id_resource

    def set_created_at(self, new_created_at):
        self.created_at = new_created_at

    def set_updated_at(self, new_updated_at):
        self.updated_at = new_updated_at

    def set_deleted_at(self, new_deleted_at):
        self.deleted_at = new_deleted_at
