import os
from app.db.models.resource import Resource  # đảm bảo bạn đã có model Resource
from sqlalchemy.orm import Session

def seed_resources(db: Session):
    raw_resources = os.getenv("DEFAULT_RESOURCES", "project,account,donation,project_collaborator")
    resource_names = [r.strip() for r in raw_resources.split(",") if r.strip()]

    for name in resource_names:
        existing = db.query(Resource).filter_by(name=name).first()
        if not existing:
            db.add(Resource(name=name))

    db.commit()
    print("Seeded resources thành công.")
