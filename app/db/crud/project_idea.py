from sqlalchemy.orm import Session
from app.db.models.project_idea import ProjectIdea
from datetime import datetime

def create_project_idea(db: Session, id_account: str, id_project: str, description: str):
    new_project_idea = ProjectIdea(
        id_account=id_account,
        id_project=id_project,
        description=description,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(new_project_idea)
    db.commit()
    db.refresh(new_project_idea)
    return new_project_idea

