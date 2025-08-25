from datetime import date
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.deps import (
    get_current_user,
    get_current_org,
    get_current_user_in_org,
    require_admin,
    get_db,
    get_pagination,
)
from app.models.user import User
from app.models.organization import Organization
from app.schemas.leave import (
    LeaveTypeCreate,
    LeaveTypeUpdate,
    LeaveTypeListResponse,
    LeaveTypePublic,
    LeaveRequestCreate,
    LeaveRequestUpdate,
    LeaveRequestListResponse,
    LeaveRequestPublic,
    AnnualBalance,
)
from app.services.leave_service import (
    create_leave_type,
    delete_leave_type,
    list_leave_types,
    update_leave_type,
    create_leave_request,
    get_leave_request,
    list_leave_requests,
    update_leave_request,
    set_leave_status,
    compute_employee_annual_balance,
)


class StatusChange(BaseModel):
    status: Literal["SUBMITTED", "APPROVED", "REJECTED", "CANCELLED"]


router = APIRouter(prefix="/hr/leaves", tags=["hr-leaves"])


# Leave Types
@router.get(
    "/types",
    response_model=LeaveTypeListResponse,
    dependencies=[Depends(get_current_user_in_org)],
)
def list_leave_types_endpoint(
    pagination: tuple[int, int] = Depends(get_pagination),
    search: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_org),
):
    page, page_size = pagination
    items, total = list_leave_types(db, page, page_size, search)
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.post(
    "/types",
    response_model=LeaveTypePublic,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user_in_org), Depends(require_admin)],
)
def create_leave_type_endpoint(
    data: LeaveTypeCreate,
    db: Session = Depends(get_db),
):
    try:
        lt = create_leave_type(db, data)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="LeaveType with this code already exists",
        )
    return lt


@router.put(
    "/types/{type_id}",
    response_model=LeaveTypePublic,
    dependencies=[Depends(get_current_user_in_org), Depends(require_admin)],
)
def update_leave_type_endpoint(
    type_id: UUID,
    data: LeaveTypeUpdate,
    db: Session = Depends(get_db),
):
    try:
        lt = update_leave_type(db, type_id, data)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="LeaveType with this code already exists",
        )
    if not lt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="LeaveType not found")
    return lt


@router.delete(
    "/types/{type_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_user_in_org), Depends(require_admin)],
)
def delete_leave_type_endpoint(
    type_id: UUID,
    db: Session = Depends(get_db),
):
    deleted = delete_leave_type(db, type_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="LeaveType not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Leave Requests
@router.get(
    "/requests",
    response_model=LeaveRequestListResponse,
    dependencies=[Depends(get_current_user_in_org)],
)
def list_leave_requests_endpoint(
    pagination: tuple[int, int] = Depends(get_pagination),
    employee_id: UUID | None = None,
    status: str | None = None,
    type_id: UUID | None = None,
    date_from: date | None = Query(None, alias="from"),
    date_to: date | None = Query(None, alias="to"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_org),
):
    page, page_size = pagination
    items, total = list_leave_requests(
        db,
        current_user,
        current_org,
        page,
        page_size,
        employee_id=employee_id,
        status=status,
        type_id=type_id,
        date_from=date_from,
        date_to=date_to,
    )
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get(
    "/requests/{request_id}",
    response_model=LeaveRequestPublic,
    dependencies=[Depends(get_current_user_in_org)],
)
def get_leave_request_endpoint(
    request_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_org),
):
    req = get_leave_request(db, current_user, current_org, request_id)
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="LeaveRequest not found")
    return req


@router.post(
    "/requests",
    response_model=LeaveRequestPublic,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user_in_org), Depends(require_admin)],
)
def create_leave_request_endpoint(
    data: LeaveRequestCreate,
    db: Session = Depends(get_db),
):
    try:
        req = create_leave_request(db, data)
    except ValueError as e:
        if str(e) == "invalid_dates":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_dates")
        if str(e) == "overlap":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="overlap")
        raise
    return req


@router.put(
    "/requests/{request_id}",
    response_model=LeaveRequestPublic,
    dependencies=[Depends(get_current_user_in_org), Depends(require_admin)],
)
def update_leave_request_endpoint(
    request_id: UUID,
    data: LeaveRequestUpdate,
    db: Session = Depends(get_db),
):
    try:
        req = update_leave_request(db, request_id, data)
    except ValueError as e:
        if str(e) == "immutable_state":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="immutable_state")
        if str(e) == "invalid_dates":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_dates")
        if str(e) == "overlap":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="overlap")
        raise
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="LeaveRequest not found")
    return req


@router.post(
    "/requests/{request_id}/status",
    response_model=LeaveRequestPublic,
    dependencies=[Depends(get_current_user_in_org), Depends(require_admin)],
)
def change_leave_status_endpoint(
    request_id: UUID,
    body: StatusChange,
    db: Session = Depends(get_db),
):
    try:
        req = set_leave_status(db, request_id, body.status)
    except ValueError as e:
        detail = str(e)
        if detail in {"invalid_status", "insufficient_balance"}:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
        raise
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="LeaveRequest not found")
    return req


@router.get(
    "/balance/{employee_id}",
    response_model=AnnualBalance,
    dependencies=[Depends(get_current_user_in_org)],
)
def get_balance_endpoint(
    employee_id: UUID,
    year: int = Query(date.today().year, ge=2000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_org),
):
    if getattr(current_user, "role", None) != "admin" and getattr(
        current_user, "employee_id", None
    ) != employee_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="LeaveRequest not found"
        )
    balance = compute_employee_annual_balance(db, employee_id, year)
    return balance
