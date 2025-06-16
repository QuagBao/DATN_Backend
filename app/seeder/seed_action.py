import os
from sqlalchemy.orm import Session
from app.db.models.action import Action  # Đảm bảo bạn đã có Action model

def seed_actions(db: Session):
    raw_actions = os.getenv("DEFAULT_ACTIONS", "add,update,delete,read")
    actions = [a.strip() for a in raw_actions.split(",") if a.strip()]

    for action_name in actions:
        existing = db.query(Action).filter_by(name=action_name).first()
        if not existing:
            db.add(Action(name=action_name))

    db.commit()
    print("✅ Default actions seeded.")
