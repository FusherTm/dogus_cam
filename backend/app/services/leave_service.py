from datetime import date
from decimal import Decimal
from typing import Sequence
from uuid import UUID

from sqlalchemy import or_, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.leave_type import LeaveType
from app.models.leave_request import LeaveRequest
from app.models.user import User
from app.models.organization import Organization
from uuid import uuid4
from app.schemas.leave import (
    LeaveTypeCreate,
    LeaveTypeUpdate,
    LeaveRequestCreate,
    LeaveRequestUpdate,
)


def _calc_days(start_date: date, end_date: date) -> Decimal:
    if start_date > end_date:
        raise ValueError("invalid_dates")
    return Decimal((end_date - start_date).days + 1)


def create_leave_type(db: Session, data: LeaveTypeCreate) -> LeaveType:
    lt = LeaveType(**data.model_dump())
    db.add(lt)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(lt)
    return lt


def list_leave_types(
    db: Session, page: int, page_size: int, search: str | None = None
) -> tuple[Sequence[LeaveType], int]:
    query = db.query(LeaveType)
    if search:
        like = f"%{search}%"
        query = query.filter(or_(LeaveType.code.ilike(like), LeaveType.name.ilike(like)))
    total = query.count()
    items = (
        query.order_by(LeaveType.created_at_utc.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def get_leave_type(db: Session, id: UUID) -> LeaveType | None:
    return db.get(LeaveType, id)


def update_leave_type(db: Session, id: UUID, data: LeaveTypeUpdate) -> LeaveType | None:
    lt = db.get(LeaveType, id)
    if not lt:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(lt, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(lt)
    return lt


def delete_leave_type(db: Session, id: UUID) -> bool:
    lt = db.get(LeaveType, id)
    if not lt:
        return False
    db.delete(lt)
    db.commit()
    return True


def create_leave_request(db: Session, data: LeaveRequestCreate) -> LeaveRequest:
    days = _calc_days(data.start_date, data.end_date)
    overlap = (
        db.query(LeaveRequest)
        .filter(
            LeaveRequest.employee_id == data.employee_id,
            LeaveRequest.status.in_(["SUBMITTED", "APPROVED"]),
            LeaveRequest.start_date <= data.end_date,
            LeaveRequest.end_date >= data.start_date,
        )
        .first()
    )
    if overlap:
        raise ValueError("overlap")
    req = LeaveRequest(
        id=uuid4(),
        employee_id=data.employee_id,
        type_id=data.type_id,
        start_date=data.start_date,
        end_date=data.end_date,
        days=days,
        reason=data.reason,
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


def get_leave_request(
    db: Session, current_user: User, current_org: Organization, id: UUID
) -> LeaveRequest | None:
    query = db.query(LeaveRequest).filter(LeaveRequest.id == id)
    if hasattr(LeaveRequest, "org_id"):
        query = query.filter(LeaveRequest.org_id == current_org.id)
    if getattr(current_user, "role", None) != "admin":
        emp_id = getattr(current_user, "employee_id", None)
        query = query.filter(LeaveRequest.employee_id == emp_id)
    return query.first()


def update_leave_request(
    db: Session, id: UUID, data: LeaveRequestUpdate
) -> LeaveRequest | None:
    req = db.get(LeaveRequest, id)
    if not req:
        return None
    if req.status != "DRAFT":
        raise ValueError("immutable_state")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(req, field, value)
    if data.start_date is not None or data.end_date is not None:
        req.days = _calc_days(req.start_date, req.end_date)
        overlap = (
            db.query(LeaveRequest)
            .filter(
                LeaveRequest.id != req.id,
                LeaveRequest.employee_id == req.employee_id,
                LeaveRequest.status.in_(["SUBMITTED", "APPROVED"]),
                LeaveRequest.start_date <= req.end_date,
                LeaveRequest.end_date >= req.start_date,
            )
            .first()
        )
        if overlap:
            db.rollback()
            # reset to original? but we already changed fields; easier to raise after rollback
            raise ValueError("overlap")
    db.commit()
    db.refresh(req)
    return req


def _is_transition_allowed(current: str, new: str) -> bool:
    transitions = {
        "DRAFT": {"SUBMITTED", "CANCELLED"},
        "SUBMITTED": {"APPROVED", "REJECTED", "CANCELLED"},
        "APPROVED": set(),
        "REJECTED": set(),
        "CANCELLED": set(),
    }
    return new in transitions.get(current, set())


def compute_employee_annual_balance(
    db: Session, employee_id: UUID, year: int
) -> dict[str, Decimal]:
    from app.models.employee import Employee  # local import to avoid circular

    employee = db.get(Employee, employee_id)
    if not employee:
        base = Decimal("0")
    else:
        base = employee.annual_leave_days_per_year
    start = date(year, 1, 1)
    end = date(year, 12, 31)
    used = (
        db.query(func.coalesce(func.sum(LeaveRequest.days), 0))
        .join(LeaveType, LeaveRequest.type_id == LeaveType.id)
        .filter(
            LeaveRequest.employee_id == employee_id,
            LeaveRequest.status == "APPROVED",
            LeaveType.is_annual.is_(True),
            LeaveRequest.start_date >= start,
            LeaveRequest.start_date <= end,
        )
        .scalar()
    )
    used = Decimal(used or 0)
    remaining = base - used
    if remaining < 0:
        remaining = Decimal("0")
    return {"employee_id": employee_id, "year": year, "base": base, "used": used, "remaining": remaining}


def set_leave_status(db: Session, id: UUID, new_status: str) -> LeaveRequest | None:
    req = db.get(LeaveRequest, id)
    if not req:
        return None
    if not _is_transition_allowed(req.status, new_status):
        raise ValueError("invalid_status")
    if new_status == "APPROVED":
        lt = db.get(LeaveType, req.type_id)
        if lt and lt.is_annual:
            balance = compute_employee_annual_balance(db, req.employee_id, req.start_date.year)
            if req.days > balance["remaining"]:
                raise ValueError("insufficient_balance")
    req.status = new_status
    db.commit()
    db.refresh(req)
    return req


def list_leave_requests(
    db: Session,
    current_user: User,
    current_org: Organization,
    page: int,
    page_size: int,
    employee_id: UUID | None = None,
    status: str | None = None,
    type_id: UUID | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> tuple[Sequence[LeaveRequest], int]:
    query = db.query(LeaveRequest)
    if hasattr(LeaveRequest, "org_id"):
        query = query.filter(LeaveRequest.org_id == current_org.id)
    if getattr(current_user, "role", None) != "admin":
        emp_id = getattr(current_user, "employee_id", None)
        query = query.filter(LeaveRequest.employee_id == emp_id)
    elif employee_id:
        query = query.filter(LeaveRequest.employee_id == employee_id)
    if status:
        query = query.filter(LeaveRequest.status == status)
    if type_id:
        query = query.filter(LeaveRequest.type_id == type_id)
    if date_from:
        query = query.filter(LeaveRequest.start_date >= date_from)
    if date_to:
        query = query.filter(LeaveRequest.end_date <= date_to)
    total = query.count()
    items = (
        query.order_by(LeaveRequest.created_at_utc.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total
