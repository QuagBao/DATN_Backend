import uuid
from sqlalchemy import Column, String
from sqlalchemy import String
from sqlalchemy.orm import relationship
from app.db.database import Base

class Resource(Base):
    __tablename__ = "resources"

    id_resource = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)

    permissions = relationship("Permission", back_populates="resource")

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"<Resource(id='{self.id_resource}', name='{self.name}')>"

    # Getter
    def get_name(self):
        return self.name

    # Setter
    def set_name(self, new_name):
        self.name = new_name
