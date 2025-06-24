from fastapi import Form, UploadFile, File, Depends, HTTPException, APIRouter, Response
from sqlalchemy.orm import Session
import json
from app.db.schemas.request.project_request import project_create, project_update
from app.db.schemas.request.account_request import admin_update
from app.db.schemas.response.project_response import ProjectOut, ProjectWithStats
from app.db.crud.project import get_total_collaborators_and_donors_by_project
from app.db.database import get_db
from app.db.crud.auth import require_roles
from app.db.crud.project import update_project, get_projects_by_owner, get_project_by_owner_and_name
from app.db.crud.staff import create_staff, get_staff_by_id, delete_staff , get_all_staff, get_all_users
from app.db.crud.permission import get_all_permissions
from app.db.crud.resource import get_resource_name_by_permission
from app.db.crud.action import get_action_name_by_permission
from app.db.crud.role import get_role_by_name, get_permission_ids_by_role_id, set_permissions_for_role_id
from app.db.crud.account import update_admin_info
from app.db.crud.collaborator import get_collaborator_by_id, update_status_collaborator, delete_collaborator_by_id
from app.db.schemas.response.paginated_response import PaginatedResponse  # nếu có
from app.db.models.project_collaborator import ProjectCollaborator
from app.db.models.donation import Donation
from app.db.crud import project as crud_project
from math import ceil
from app.db.schemas.response.account_response import account_out
import io
from app.db.crud.collaborator import get_collaborator_by_project_id
from app.db.crud.donation import get_donation_by_project_id, get_all_donations
from typing import List, Optional
from datetime import datetime
from app.db.crud.account import get_account_by_id
from urllib.parse import quote

router = APIRouter(prefix="/admin", tags=["admin"])

# ================= API: admin-info =================
@router.patch("/admin/update-profile")
def update_admin_profile(
    data: admin_update,
    db: Session = Depends(get_db),
    admin=Depends(require_roles(["admin"]))
):
    if admin.role.name != "admin":
        raise HTTPException(status_code=403, detail="Bạn không có quyền cập nhật thông tin admin")
    updated = update_admin_info(
        db,
        admin.id_account,
        full_name=data.full_name,
        phone=data.phone,
        password=data.password
    )
    if not updated:
        raise HTTPException(404, detail="Không tìm thấy tài khoản admin")
    return {"message": "Cập nhật thông tin admin thành công"}

# ================= API: project =================

@router.patch("/projects/update-by-owner")
def update_project_by_name_endpoint(
    name_project: str = Form(...),
    data: str = Form(...),
    id_images_to_keep: Optional[List[str]] = Form(None),
    images: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db),
    admin=Depends(require_roles(["admin"]))
):
    try:
        parsed_data = project_update(**json.loads(data))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Dữ liệu JSON không hợp lệ")
    if admin.role.name != "admin":
        raise HTTPException(status_code=403, detail="Bạn không có quyền cập nhật dự án")
    project = get_project_by_owner_and_name(db, admin.id_account, name_project)
    if not project:
        raise HTTPException(status_code=404, detail="Không tìm thấy dự án theo tên và chủ sở hữu")


    updated_project = update_project(db, project.id_project, parsed_data, id_images_to_keep, images)
    return {"message": "Cập nhật dự án thành công", "id_project": updated_project.id_project}

@router.get("/projects/by-owner", response_model=PaginatedResponse[ProjectWithStats])
def get_projects_by_owner_endpoint(
    page: int = 1,
    limit: int = 40,
    db: Session = Depends(get_db),
    admin = Depends(require_roles(["admin"]))
):
    if admin.role.name != "admin":
        raise HTTPException(status_code=403, detail="Bạn không có quyền xem dự án của người dùng khác")
    
    skip = (page - 1) * limit
    projects, total = get_projects_by_owner(db, owner_id=admin.id_account, skip=skip, limit=limit)
    total_pages = ceil(total / limit) if total > 0 else 1

    result = []
    for project in projects:
        total_col, total_don = get_total_collaborators_and_donors_by_project(db, project.id_project)
        result.append(ProjectWithStats(
            **ProjectOut.model_validate(project).model_dump(),
            total_collaborators=total_col,
            total_donors=total_don
        ))

    return {
        "page": page,
        "limit": limit,
        "total_items": total,
        "total_pages": total_pages,
        "data": result
    }

# ================= API: staff,user =================

@router.post("/staff/create")
def create_staff_endpoint(
    email : str,
    db : Session = Depends(get_db), 
    admin = Depends(require_roles(["admin"]))
):
    if admin.role.name != "admin":
        raise HTTPException(status_code=403, detail="Bạn không có quyền tạo nhân viên")
    staff = create_staff(db, email)
    return {"message": "Tạo nhân viên thành công"}
    
@router.delete("/staff/delete/{id_staff}")
def delete_staff_endpoint(
    id_staff: str, 
    db: Session = Depends(get_db),
    admin = Depends(require_roles(["admin"]))
):
    if admin.role.name != "admin":
        raise HTTPException(status_code=403, detail="Bạn không có quyền xóa nhân viên")
    staff = get_staff_by_id(db, id_staff)
    if not staff:
        raise HTTPException(status_code=404, detail="Không tìm thấy nhân viên")
    delete_staff(db, staff.id_account)
    return {"message": "Xóa nhân viên thành công", "id_staff": staff.id_account}

@router.get("/staff/{id_staff}", response_model=account_out)
def get_staff_by_id_endpoint(
    id_staff: str,
    db: Session = Depends(get_db),
    admin = Depends(require_roles(["admin"]))
):
    if admin.role.name != "admin":
        raise HTTPException(status_code=403, detail="Bạn không có quyền xem thông tin nhân viên")
    staff = get_staff_by_id(db, id_staff)
    if not staff:
        raise HTTPException(status_code=404, detail="Không tìm thấy nhân viên")
    return staff

@router.get("/staff", response_model=PaginatedResponse[account_out])
def get_all_staff_endpoint(
    page: int = 1,
    limit: int = 40,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[str] = None,
    universal_search: Optional[str] = None,
    db: Session = Depends(get_db),
    admin = Depends(require_roles(["admin"]))
):
    if admin.role.name != "admin":
        raise HTTPException(status_code=403, detail="Bạn không có quyền xem danh sách nhân viên")
    if page < 1:
        raise HTTPException(status_code=400, detail="Page phải lớn hơn 0")
    # Parse start_date và end_date
    start = None
    end = None
    try:
        if start_date:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
        if end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="start_date/end_date phải đúng định dạng YYYY-MM-DD")
    skip = (page - 1) * limit
    staff_list, total = get_all_staff(
        db,
        skip=skip,
        limit=limit,
        universal_search=universal_search,
        start_date=start,
        end_date=end,
        status=status
    )
    total_pages = ceil(total / limit)
    return {
        "page": page,
        "limit": limit,
        "total_items": total,
        "total_pages": total_pages,
        "data": staff_list
    }
    
@router.get("/users", response_model=PaginatedResponse[account_out])
def get_all_users_endpoint(
    page: int = 1,
    limit: int = 40,
    universal_search: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    admin = Depends(require_roles(["admin"]))
):
    if admin.role.name != "admin":
        raise HTTPException(status_code=403, detail="Bạn không có quyền xem danh sách người dùng")
    if page < 1:
        raise HTTPException(status_code=400, detail="Page phải lớn hơn 0")
    # Parse start_date và end_date
    start = None
    end = None
    try:
        if start_date:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
        if end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="start_date và end_date phải đúng định dạng YYYY-MM-DD")
    skip = (page - 1) * limit
    users, total = get_all_users(
        db,
        skip=skip,
        limit=limit,
        universal_search=universal_search,
        start_date=start,
        end_date=end,
        status=status
    )
    total_pages = ceil(total / limit)
    return {
        "page": page,
        "limit": limit,
        "total_items": total,
        "total_pages": total_pages,
        "data": users
    }
    
@router.patch("/block-user/{id_account}")
def block_user_endpoint(
    id_account: str,
    db: Session = Depends(get_db),
    admin=Depends(require_roles(["admin"]))
):
    if admin.role.name != "admin":
        raise HTTPException(status_code=403, detail="Bạn không có quyền khóa người dùng")
    user = get_account_by_id(db, id_account)
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    user.status = "blocked"
    db.commit()
    return {"message": "Đã khóa người dùng", "id_user": id_account}

@router.patch("/unblock-user/{id_account}")
def unblock_user_endpoint(
    id_account: str,
    db: Session = Depends(get_db),
    admin=Depends(require_roles(["admin"]))
):
    if admin.role.name != "admin":
        raise HTTPException(status_code=403, detail="Bạn không có quyền mở khóa người dùng")
    user = get_account_by_id(db, id_account)
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    user.status = "active"
    db.commit()
    return {"message": "Đã mở khóa người dùng", "id_user": id_account}

#================= API: permissions =================
# @router.get("/permissions/dashboard")
# def get_permission_matrix(
#     db: Session = Depends(get_db),
#     admin = Depends(require_roles(["admin"]))
# ):
#     if admin.role.name != "admin":
#         raise HTTPException(status_code=403, detail="Bạn không có quyền xem danh sách quyền")
#     permissions = get_all_permissions(db)
#     result = []
#     for perm in permissions:
#         resource = get_resource_name_by_permission(db, perm.id_permission)
#         if not resource:
#             raise HTTPException(status_code=404, detail="Không tìm thấy resource")
#         action = get_action_name_by_permission(db, perm.id_permission)
#         if not action:
#             raise HTTPException(status_code=404, detail="Không tìm thấy action")
#         result.append({
#             "id_permission": perm.id_permission,
#             "resource": resource.name,
#             "action": action.name
#         })
#     return result

# @router.get("/roles/{role_name}/permissions")
# def get_permissions_of_role(role_name: str, 
#                             db: Session = Depends(get_db),
#                             admin=Depends(require_roles(["admin"]))):
#     if admin.role.name != "admin":
#         raise HTTPException(status_code=403, detail="Bạn không có quyền xem danh sách quyền")
#     role = get_role_by_name(db, role_name)
#     if not role:
#         raise HTTPException(404, "Không tìm thấy role")

#     return get_permission_ids_by_role_id(db, role.id_role)

# @router.post("/roles/{role_name}/set-permissions")
# def set_permissions_for_role(
#     role_name: str,
#     permissions: list[str] = Form(...),
#     db: Session = Depends(get_db),
#     admin=Depends(require_roles(["admin"]))
# ):
#     if admin.role.name != "admin":
#         raise HTTPException(status_code=403, detail="Bạn không có quyền cập nhật quyền")
#     role = get_role_by_name(db, role_name)
#     if not role:
#         raise HTTPException(404, "Không tìm thấy role")

#     set_permissions_for_role_id(db, role.id_role, permissions)
#     return {"message": "Cập nhật quyền thành công"}

# ================= API: collaborator =================

@router.patch("/accept-collaborators/{id_collaborator}")
def accept_collaborator(
    id_collaborator: str,
    db: Session = Depends(get_db),
    admin=Depends(require_roles(["admin"]))
):
    if admin.role.name != "admin":
        raise HTTPException(status_code=403, detail="Bạn không có quyền chấp nhận cộng tác viên")
    collaborator = get_collaborator_by_id(db, id_collaborator)
    if not collaborator:
        raise HTTPException(status_code=404, detail="Không tìm thấy cộng tác viên")
    check = update_status_collaborator(db, id_collaborator)
    if not check:
        raise HTTPException(status_code=404, detail="Cập nhật trạng thái cộng tác viên không thành công")
    return {"message": "Cập nhật trạng thái cộng tác viên thành công", "id_collaborator": id_collaborator}

@router.delete("/collaborators/{id_collaborator}")
def delete_collaborator(
    id_collaborator: str,
    db: Session = Depends(get_db),
    admin=Depends(require_roles(["admin"]))
):
    if admin.role.name != "admin":
        raise HTTPException(status_code=403, detail="Bạn không có quyền xóa cộng tác viên")
    collaborator = get_collaborator_by_id(db, id_collaborator)
    if not collaborator:
        raise HTTPException(status_code=404, detail="Không tìm thấy cộng tác viên")
    success = delete_collaborator_by_id(db, id_collaborator)
    if not success:
        raise HTTPException(status_code=404, detail="Không tìm thấy cộng tác viên")
    return {"message": "Đã xóa cộng tác viên", "id_collaborator": id_collaborator}



# ================= API: Export CSV  =================
@router.get("/collaborators/export")
def export_collaborators_csv(
    id_project: str,
    db: Session = Depends(get_db),
    admin=Depends(require_roles(["admin"]))
):
    if admin.role.name != "admin":
        raise HTTPException(status_code=403, detail="Bạn không có quyền xuất danh sách cộng tác viên")
    collaborators = get_collaborator_by_project_id(db, id_project)
    if not collaborators:
        raise HTTPException(status_code=404, detail="Không có cộng tác viên nào để xuất")
    name_project = collaborators[0].project.name_project
    # Tạo CSV
    output = io.StringIO()
    output.write("Họ và tên,Email,Số điện thoại,Ngày nộp đơn,Ngày phê duyệt\n")
    for col in collaborators:
        output.write(
            f"{col.full_name or ''},"
            f"{col.email or ''},"
            f"{col.phone or ''},"
            f"{col.applied_at or ''},"
            f"{col.approved_at or ''},\n"
        )
    csv_data = output.getvalue()
    output.close()
    bom = '\ufeff'
    csv_with_bom = bom + csv_data
    csv_bytes = csv_with_bom.encode("utf-8")
    filename = f"collaborators_{name_project}.csv"
    filename_enc = quote(filename, safe="")
    content_disp = f"attachment; filename*=UTF-8''{filename_enc}"
    return Response(
        content=csv_bytes,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": content_disp}
    )

@router.post("/collaborators/import")
def import_collaborators_csv(
    id_project: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin=Depends(require_roles(["admin"]))
):
    if admin.role.name != "admin":
        raise HTTPException(status_code=403, detail="Bạn không có quyền import cộng tác viên")
    if file.content_type != "text/csv":
        raise HTTPException(status_code=400, detail="File phải là CSV")
    content = file.file.read().decode("utf-8-sig").splitlines()
    header = content[0].strip().split(",")
    rows = content[1:]
    if header != ["Họ và tên", "Email", "Số điện thoại"]:
        raise HTTPException(status_code=400, detail="CSV không đúng định dạng header")
    count = 0
    for row in rows:
        fields = row.strip().split(",")
        if len(fields) != 3:
            continue
        full_name, email, phone = fields

        # Tạo collaborator mới
        collaborator = ProjectCollaborator(
            account_id=None,
            project_id=id_project,
            full_name=full_name.strip(),
            email=email.strip(),
            phone=phone.strip(),
            status="pending",
            applied_at=datetime.utcnow()
        )
        db.add(collaborator)
        count += 1

    db.commit()

    return {"message": f"Đã import {count} cộng tác viên thành công"}

    
@router.get("/donations/export")
def export_donations_csv(
    id_project: str,
    db: Session = Depends(get_db),
    admin=Depends(require_roles(["admin"]))
):
    if admin.role.name != "admin":
        raise HTTPException(status_code=403, detail="Bạn không có quyền xuất danh sách quyên góp")
    # Lấy danh sách donation theo project
    donations = get_donation_by_project_id(db, id_project)
    if not donations:
        raise HTTPException(status_code=404, detail="Không có quyên góp nào để xuất")
    name_project = donations[0].project.name_project
    # Tạo CSV
    output = io.StringIO()
    output.write("Họ và tên,Email,Số điện thoại,Số tiền,Thời gian thanh toán,Mã giao dịch\n")
    for donation in donations:
        output.write(
            f"{donation.full_name or ''},"
            f"{donation.email or ''},"
            f"{donation.phone or ''},"
            f"{donation.amount},"
            f"{donation.paytime},"
            f"{donation.transaction_id}\n"
        )
    csv_data = output.getvalue()
    output.close()
    # Thêm BOM để Excel đọc đúng
    bom = '\ufeff'
    csv_with_bom = bom + csv_data
    csv_bytes = csv_with_bom.encode("utf-8")
    filename = f"donations_{name_project}.csv"
    filename_enc = quote(filename, safe="")
    content_disp = f"attachment; filename*=UTF-8''{filename_enc}"
    return Response(
        content=csv_bytes,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": content_disp}
    )

@router.post("/donations/import")
def import_donations_csv(
    id_project: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin=Depends(require_roles(["admin"]))
):
    if admin.role.name != "admin":
        raise HTTPException(status_code=403, detail="Bạn không có quyền import donation")

    if file.content_type != "text/csv":
        raise HTTPException(status_code=400, detail="File phải là CSV")

    content = file.file.read().decode("utf-8-sig").splitlines()
    header = content[0].strip().split(",")
    rows = content[1:]

    if header != ["full_name", "email", "phone", "amount", "paytime", "transaction_id"]:
        raise HTTPException(status_code=400, detail="CSV không đúng định dạng header")

    count = 0
    for row in rows:
        fields = row.strip().split(",")
        if len(fields) != 6:
            continue
        full_name, email, phone, amount, paytime, transaction_id = fields

        # Tạo donation mới
        donation = Donation(
            project_id=id_project,
            full_name=full_name.strip(),
            email=email.strip(),
            phone=phone.strip(),
            amount=float(amount),
            paytime=paytime.strip(),
            transaction_id=transaction_id.strip()
        )
        db.add(donation)

        # Cập nhật số tiền hiện tại & số lượt ủng hộ của project
        current_numeric = crud_project.get_current_numeric_by_project(db=db, id_project=donation.project_id)
        current_numeric += donation.amount
        crud_project.update_current_numeric(db=db, id_project=donation.project_id, new_numeric=current_numeric)
        
        count += 1

    db.commit()

    return {"message": f"Đã import {count} lượt ủng hộ thành công"}
