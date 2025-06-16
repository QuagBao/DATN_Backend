import uuid
from sqlalchemy import Column, TIMESTAMP, ForeignKey
from sqlalchemy import String, Integer
from sqlalchemy.orm import relationship
from app.db.database import Base

class ProjectIdea(Base):
    
    __tablename__ = "project_ideas"

    id_project_idea = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    id_account = Column(String(36), ForeignKey("account.id_account"))
    id_project = Column(String(36), ForeignKey("project.id_project"))
    description = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False)
    
    # Relationships
    account = relationship("Account", back_populates="project_ideas")
    project = relationship("Project", back_populates="project_ideas")
    
    def __init__(self, id_account, id_project, description, created_at=None, updated_at=None):
        self.id_account = id_account
        self.id_project = id_project
        self.description = description
        self.created_at = created_at
        self.updated_at = updated_at
        
    def __repr__(self):
        return f"<ProjectIdea(id='{self.id_project_idea}', description='{self.description}')>"
    
    # Getters
    def get_id_account(self):
        return self.id_account
    
    def get_id_project(self):
        return self.id_project
    
    def get_description(self):
        return self.description
    
    def get_created_at(self):
        return self.created_at
    
    def get_updated_at(self):
        return self.updated_at
    
    # Setters
    def set_id_account(self, new_id_account):
        self.id_account = new_id_account
        
    def set_id_project(self, new_id_project):
        self.id_project = new_id_project
        
    def set_description(self, new_description):
        self.description = new_description
        
    def set_created_at(self, new_created_at):
        self.created_at = new_created_at
        
    def set_updated_at(self, new_updated_at):
        self.updated_at = new_updated_at
        
    def set_deleted_at(self, new_deleted_at):
        self.deleted_at = new_deleted_at
    