import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import relationship
from app.db.database import Base

class Image(Base):
    __tablename__ = "images"

    id_image = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    url = Column(String(255), nullable=False)
    id_project = Column(String(36), ForeignKey("project.id_project", ondelete="CASCADE"))
    
    project = relationship("Project", back_populates="images")

    def __init__(self, url, id_project):
        self.url = url
        self.id_project = id_project

    def __repr__(self):
        return f"<Image(id='{self.id_image}', url='{self.url}')>"
