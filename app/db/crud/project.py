# app/db/crud/project.py
from app.db.models import Project, Image, ProjectCollaborator, Donation
from sqlalchemy.orm import Session
import uuid, os, shutil
from fastapi import UploadFile
from datetime import datetime
from typing import Optional, List
from datetime import date
from sqlalchemy import and_

def create_project(db: Session, data, images: List[UploadFile], id_owner: str):
    # 1. Parse ngày
    start = datetime.strptime(data.start_date, "%Y-%m-%d").date()
    end = datetime.strptime(data.end_date, "%Y-%m-%d").date()

    # 2. Tạo project
    new_project = Project(
        name_project=data.name_project,
        description=data.description,
        content=data.content,
        status="IN_PROGRESS",
        start_date=start,
        end_date=end,
        current_numeric=0.0,
        total_numeric=data.total_numeric,
        id_owner=id_owner
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    # 3. Tạo thư mục nếu chưa tồn tại
    image_dir = "static/images"
    os.makedirs(image_dir, exist_ok=True)
    # 4. Lưu từng ảnh vào thư mục + tạo bản ghi Image
    for image in images:
        ext = os.path.splitext(image.filename)[1]
        image_filename = f"{uuid.uuid4()}{ext}"
        image_path = os.path.join(image_dir, image_filename)
        with open(image_path, "wb") as f:
            shutil.copyfileobj(image.file, f)
        image_db = Image(url=image_path, id_project=new_project.id_project)
        db.add(image_db)
    # 5. Commit ảnh sau khi add tất cả
    db.commit()
    return new_project

def update_expired_projects(db: Session, today: date) -> int:
    # Update project nào có end_date < hôm nay, status chưa là EXPIRED
    expired_projects = db.query(Project).filter(
        Project.end_date < today,
        Project.status != "EXPIRED"
    ).all()
    for project in expired_projects:
        project.status = "EXPIRED"
    db.commit()
    return len(expired_projects)


def update_project(db: Session, id_project: str, data, id_images_to_keep: Optional[List[str]] = None, images: Optional[List[UploadFile]] = None):
    project = db.query(Project).filter(Project.id_project == id_project).first()
    if not project:
        return None
    # 1. Cập nhật các trường nếu có
    if data.name_project is not None:
        project.name_project = data.name_project
    if data.description is not None:
        project.description = data.description
    if data.content is not None:
        project.content = data.content
    if data.start_date is not None:
        project.start_date = datetime.strptime(data.start_date, "%Y-%m-%d").date()
    if data.end_date is not None:
        project.end_date = datetime.strptime(data.end_date, "%Y-%m-%d").date()
    if data.total_numeric is not None:
        project.total_numeric = data.total_numeric
        
    # 2. Xử lý ảnh cũ
    if id_images_to_keep is None:
        id_images_to_keep = []
 
    # Lấy tất cả ảnh cũ của dự án
    old_images = db.query(Image).filter(Image.id_project == id_project).all()

    # Xóa ảnh cũ không nằm trong danh sách giữ lại
    for img in old_images:
        if img.id_image not in id_images_to_keep:
            try:
                if os.path.exists(img.url):
                    os.remove(img.url)
            except Exception as e:
                print(f"Lỗi khi xoá ảnh cũ: {e}")
            db.delete(img)

    # 3. Thêm tất cả ảnh mới upload (nếu có)
    if images:
        os.makedirs("static/images", exist_ok=True)
        for image in images:
            ext = os.path.splitext(image.filename)[1]
            image_path = f"static/images/{str(uuid.uuid4())}{ext}"
            with open(image_path, "wb") as f:
                shutil.copyfileobj(image.file, f)
            new_image = Image(url=image_path, id_project=project.id_project)
            db.add(new_image)

    # if image:
    #     # Xoá ảnh cũ trong bảng Image và file cũ nếu có
    #     old_image = db.query(Image).filter(Image.id_project == id_project).first()
    #     if old_image:
    #         try:
    #             if os.path.exists(old_image.url):
    #                 os.remove(old_image.url)
    #         except Exception as e:
    #             print(f"Lỗi khi xoá ảnh cũ: {e}")
    #         db.delete(old_image)
    #         db.commit()
    #     # Lưu ảnh mới
    #     ext = os.path.splitext(image.filename)[1]
    #     image_path = f"static/images/{str(uuid.uuid4())}{ext}"
    #     os.makedirs("static/images", exist_ok=True)
    #     with open(image_path, "wb") as f:
    #         shutil.copyfileobj(image.file, f)
    #     # Tạo bản ghi ảnh mới
    #     new_image = Image(url=image_path, id_project=project.id_project)
    #     db.add(new_image)
    db.commit()
    db.refresh(project)
    return project

def delete_project(db: Session, id_project: str):
    # 1. Tìm project
    project = db.query(Project).filter(Project.id_project == id_project).first()
    if not project:
        return None
    # 2. Tìm ảnh liên quan
    images = db.query(Image).filter(Image.id_project == id_project).all()
    for img in images:
        # Xoá tệp vật lý nếu tồn tại
        if os.path.exists(img.url):
            try:
                os.remove(img.url)
            except Exception as e:
                print(f"Lỗi khi xoá ảnh: {e}")
        # Xoá bản ghi ảnh
        db.delete(img)
    # 3. Xoá project
    db.delete(project)
    db.commit()
    return True

def get_project_by_id(db: Session, id_project: str):
    project = db.query(Project).filter(Project.id_project == id_project).first()
    if not project:
        return None
    return project

def get_project_by_owner_and_name(db: Session, id_owner: str, name_project: str):
    return db.query(Project).filter(
        Project.id_owner == id_owner,
        Project.name_project == name_project
    ).first()

def get_projects_by_owner(db: Session, id_owner: str, skip=0, limit=40):
    query = db.query(Project).filter(Project.id_owner == id_owner)
    total = query.count()
    projects = query.offset(skip).limit(limit).all()
    return projects, total


def get_all_projects(
    db: Session,
    skip: int = 0,
    limit: int = 40,
    name_project: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    status: Optional[str] = None
):
    query = db.query(Project)
    filters = []
    if name_project:
        filters.append(Project.name_project.ilike(f"%{name_project}%"))
    if start_date and end_date:
        filters.append(Project.start_date <= end_date)
        filters.append(Project.end_date >= start_date)
    elif start_date:
        filters.append(Project.end_date >= start_date)
    elif end_date:
        filters.append(Project.start_date <= end_date)
    if status:
        filters.append(Project.status.ilike(f"%{status}%"))  # giả sử tiến độ lưu dưới dạng chuỗi
    if filters:
        query = query.filter(and_(*filters))

    total = query.count()
    projects = query.offset(skip).limit(limit).all()

    return projects, total

def get_projects_in_progress(db: Session, skip: int = 0, limit: int = 40):
    query = db.query(Project).filter(Project.status == "IN_PROGRESS")
    total = query.count()
    projects = query.offset(skip).limit(limit).all()
    return projects, total

def get_total_collaborators_and_donors(db: Session):
    # Tổng số account_id duy nhất trong project_collaborator
    total_collaborators = db.query(ProjectCollaborator.id).filter(ProjectCollaborator.status == "active").distinct().count()
    # Tổng số transaction_id duy nhất trong donation
    total_donors = db.query(Donation.transaction_id).distinct().count()
    # Tổng số project_id duy nhất trong project 
    total_projects = db.query(Project.id_project).distinct().count()
    return {
        "total_projects": total_projects,
        "total_collaborators": total_collaborators,
        "total_donors": total_donors
    }

def get_total_collaborators_and_donors_by_project(db: Session, id_project: str):
    # Tổng số id duy nhất trong project_collaborator
    total_collaborators = db.query(ProjectCollaborator.id).filter(ProjectCollaborator.project_id == id_project).filter(ProjectCollaborator.status == "active").distinct().count()
    # Tổng số transaction_id duy nhất trong donation
    total_donors = db.query(Donation.transaction_id).filter(Donation.project_id == id_project).distinct().count()
    return total_collaborators, total_donors

def get_current_numeric_by_project(db: Session, id_project: str):
    # Lấy current_numeric của project
    project = db.query(Project).filter(Project.id_project == id_project).first()
    if not project:
        return None
    return project.current_numeric

def update_current_numeric(db: Session, id_project: str, new_numeric: float):
    # Cập nhật current_numeric của project
    project = db.query(Project).filter(Project.id_project == id_project).first()
    if not project:
        return None
    project.current_numeric = new_numeric
    db.commit()
    db.refresh(project)
    return project

def delete_image_by_id_project(db: Session, id_project: str):
    # Tìm tất cả ảnh liên quan đến project
    images = db.query(Image).filter(Image.id_project == id_project).all()
    for img in images:
        # Xoá tệp vật lý nếu tồn tại
        if os.path.exists(img.url):
            try:
                os.remove(img.url)
            except Exception as e:
                print(f"Lỗi khi xoá ảnh: {e}")
        # Xoá bản ghi ảnh
        db.delete(img)
    db.commit()
    return True