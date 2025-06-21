import uuid
from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, func
from sqlalchemy import String
from sqlalchemy.orm import relationship
from app.db.database import Base
from sqlalchemy import Integer


class Account(Base):
    __tablename__ = "account"

    id_account = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    id_role = Column(Integer, ForeignKey("roles.id_role", ondelete="SET NULL"), nullable=True)
  
    password = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(255), nullable=True)
    full_name = Column(String(255), nullable=True)
    status = Column(String(255), nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationship
    role = relationship("Role", back_populates="accounts")
    owned_projects = relationship("Project", back_populates="owner")
    project_ideas = relationship("ProjectIdea", back_populates="account")
        
    def __init__(self, password, email, phone=None, full_name=None, status=None, id_role=None):
        self.password = password
        self.email = email
        self.phone = phone
        self.full_name = full_name
        self.status = status
        self.id_role = id_role

    def __repr__(self):
        return f"<Account(id='{self.id_account}', email='{self.email}')>"

    # Getters

    def get_email(self):
        return self.email

    def get_full_name(self):
        return self.full_name

    def get_status(self):
        return self.status

    # Setters
    def set_password(self, new_password):
        self.password = new_password

    def set_phone(self, new_phone):
        self.phone = new_phone

    def set_status(self, new_status):
        self.status = new_status

    def set_full_name(self, new_full_name):
        self.full_name = new_full_name