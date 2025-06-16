import uuid
from sqlalchemy import Column, String, ForeignKey, TIMESTAMP, func
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy import Date, Float, Text
from app.db.database import Base


class Project(Base):
    __tablename__ = "project"

    id_owner = Column(String(36), ForeignKey("account.id_account", ondelete="CASCADE"))
    name_project = Column(String(255),unique=True, nullable=False)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    id_project = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    status = Column(String(255), nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    current_numeric = Column(Float, nullable=False, default=0.0)
    total_numeric = Column(Float, nullable=False)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


    # Relationships
    owner = relationship("Account", back_populates="owned_projects")
    donations = relationship("Donation", back_populates="project")
    collaborators = relationship("ProjectCollaborator", back_populates="project")
    images = relationship("Image", back_populates="project")
    project_ideas = relationship("ProjectIdea", back_populates="project")

    def __init__(self, name_project, id_owner, description=None, content=None, status=None, start_date=None, end_date=None,current_numeric = 0.0 ,total_numeric=0.0):
        self.name_project = name_project
        self.description = description
        self.content = content
        self.id_owner = id_owner
        self.status = status
        self.start_date = start_date
        self.end_date = end_date
        self.current_numeric = current_numeric
        self.total_numeric = total_numeric


    def __repr__(self):
        return (
        f"<Project(id='{self.id_project}', name='{self.name_project}', "
        f"owner_id='{self.id_owner}', start='{self.start_date}', end='{self.end_date}', "
        f"target={self.total_numeric})>"
    )

    # Getters
    def get_start_date(self):
        return self.start_date

    def get_end_date(self):
        return self.end_date

    def get_total_numeric(self):
        return self.total_numeric
    
    def get_name(self):
        return self.name_project

    def get_description(self):
        return self.description

    def get_owner_id(self):
        return self.id_owner

    # Setters
    def set_name(self, new_name):
        self.name_project = new_name

    def set_description(self, new_description):
        self.description = new_description

    def set_owner_id(self, new_owner_id):
        self.id_owner = new_owner_id

    def set_start_date(self, new_start_date):
        self.start_date = new_start_date

    def set_end_date(self, new_end_date):
        self.end_date = new_end_date

    def set_total_numeric(self, new_total_numeric):
        self.total_numeric = new_total_numeric