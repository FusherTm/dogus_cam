from typing import Sequence
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.warehouse import Warehouse
from app.schemas.warehouse import WarehouseCreate, WarehouseUpdate


def create_warehouse(db: Session, data: WarehouseCreate) -> Warehouse:
    warehouse = Warehouse(**data.model_dump())
    db.add(warehouse)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(warehouse)
    return warehouse


def get_warehouse(db: Session, id: UUID) -> Warehouse | None:
    return db.get(Warehouse, id)


def list_warehouses(
    db: Session, page: int, page_size: int, search: str | None = None
) -> tuple[Sequence[Warehouse], int]:
    query = db.query(Warehouse)
    if search:
        like = f"%{search}%"
        query = query.filter(or_(Warehouse.name.ilike(like), Warehouse.code.ilike(like)))
    total = query.count()
    items = (
        query.order_by(Warehouse.created_at_utc.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def update_warehouse(db: Session, id: UUID, data: WarehouseUpdate) -> Warehouse | None:
    warehouse = db.get(Warehouse, id)
    if not warehouse:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(warehouse, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(warehouse)
    return warehouse


def delete_warehouse(db: Session, id: UUID) -> bool:
    warehouse = db.get(Warehouse, id)
    if not warehouse:
        return False
    db.delete(warehouse)
    db.commit()
    return True
