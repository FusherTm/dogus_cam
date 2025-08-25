from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.deps import (
    get_current_admin,
    get_current_user,
    get_db,
    get_pagination,
)
from app.models.user import User
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeListResponse,
    EmployeePublic,
    EmployeeUpdate,
)
from app.services.employee_service import (
    create_employee,
    delete_employee,
    get_employee,
    list_employees,
    update_employee,
)

router = APIRouter(prefix="/hr/employees", tags=["hr-employees"])


@router.get("", response_model=EmployeeListResponse)
def list_employees_endpoint(
    pagination: tuple[int, int] = Depends(get_pagination),
    search: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    page, page_size = pagination
    items, total = list_employees(db, page, page_size, search)
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/{employee_id}", response_model=EmployeePublic)
def get_employee_endpoint(
    employee_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    employee = get_employee(db, employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found"
        )
    return employee


@router.post("", response_model=EmployeePublic, status_code=status.HTTP_201_CREATED)
def create_employee_endpoint(
    data: EmployeeCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        employee = create_employee(db, data)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee with this code or email already exists",
        )
    return employee


@router.put("/{employee_id}", response_model=EmployeePublic)
def update_employee_endpoint(
    employee_id: UUID,
    data: EmployeeUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        employee = update_employee(db, employee_id, data)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee with this code or email already exists",
        )
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found"
        )
    return employee


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee_endpoint(
    employee_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    deleted = delete_employee(db, employee_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
