import uuid
from sqlalchemy import Column, String
from sqlalchemy import String, Integer
from sqlalchemy.orm import relationship
from app.db.database import Base

class Action(Base):
    __tablename__ = "actions"

    id_action = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    
    permissions = relationship("Permission", back_populates="action")

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"<Action(id='{self.id_action}', name='{self.name}')>"

    # Getter
    def get_name(self):
        return self.name

    # Setter
    def set_name(self, new_name):
        self.name = new_name
