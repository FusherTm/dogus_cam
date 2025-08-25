from typing import Sequence
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeUpdate


def create_employee(db: Session, data: EmployeeCreate) -> Employee:
    employee = Employee(**data.model_dump())
    db.add(employee)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(employee)
    return employee


def get_employee(db: Session, id: UUID) -> Employee | None:
    return db.get(Employee, id)


def list_employees(
    db: Session, page: int, page_size: int, search: str | None = None
) -> tuple[Sequence[Employee], int]:
    query = db.query(Employee)
    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(
                Employee.code.ilike(like),
                Employee.full_name.ilike(like),
                Employee.email.ilike(like),
            )
        )
    total = query.count()
    items = (
        query.order_by(Employee.created_at_utc.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def update_employee(db: Session, id: UUID, data: EmployeeUpdate) -> Employee | None:
    employee = db.get(Employee, id)
    if not employee:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(employee, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(employee)
    return employee


def delete_employee(db: Session, id: UUID) -> bool:
    employee = db.get(Employee, id)
    if not employee:
        return False
    db.delete(employee)
    db.commit()
    return True
