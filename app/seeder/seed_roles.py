import os
from sqlalchemy.orm import Session
from app.db.models.role import Role

def seed_roles(db: Session):
    raw_roles = os.getenv("DEFAULT_ROLES", "user:3,staff:2,admin:1")
    role_entries = [r.strip() for r in raw_roles.split(",") if r.strip()]

    for entry in role_entries:
        if ":" not in entry:
            continue
        name, priority = entry.split(":")
        name = name.strip()
        priority = int(priority.strip())

        existing = db.query(Role).filter_by(name=name).first()
        if not existing:
            db.add(Role(name=name, priority=priority))

    db.commit()
    print("✅ Default roles seeded.")
