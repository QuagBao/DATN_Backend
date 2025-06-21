import uuid
from sqlalchemy import Column, TIMESTAMP, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class ProjectCollaborator(Base):
    __tablename__ = "project_collaborator"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = Column(String(36), nullable=True)
    full_name = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    project_id = Column(String(36), ForeignKey("project.id_project"))
    status = Column(String(36), nullable=False)
    applied_at = Column(TIMESTAMP, nullable=True)
    approved_at = Column(TIMESTAMP, nullable=True)

    project = relationship("Project", back_populates="collaborators")

    def __init__(self, account_id=None, full_name=None, email=None, phone=None,
                 project_id=None, status=None, applied_at=None, approved_at=None):
        self.account_id = account_id
        self.full_name = full_name
        self.email = email
        self.phone = phone
        self.project_id = project_id
        self.status = status
        self.applied_at = applied_at
        self.approved_at = approved_at

    def __repr__(self):
        return (f"<ProjectCollaborator(id='{self.id}', account_id='{self.account_id}', "
                f"full_name='{self.full_name}', email='{self.email}', phone='{self.phone}', "
                f"project_id='{self.project_id}', status='{self.status}', "
                f"applied_at={self.applied_at}, approved_at={self.approved_at})>")

    # Getters
    def get_status(self):
        return self.status

    def get_applied_at(self):
        return self.applied_at

    def get_approved_at(self):
        return self.approved_at

    # Setters
    def set_status(self, new_status):
        self.status = new_status

    def set_applied_at(self, new_applied_at):
        self.applied_at = new_applied_at

    def set_approved_at(self, new_approved_at):
        self.approved_at = new_approved_at
