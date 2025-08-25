from datetime import datetime
from decimal import Decimal
from typing import Sequence
from uuid import UUID

from sqlalchemy import case, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.stock_movement import StockMovement
from app.schemas.stock_movement import StockMovementCreate


class InsufficientStock(Exception):
    pass


def get_product_stock(
    db: Session, product_id: UUID, warehouse_id: UUID | None = None
) -> Decimal:
    query = db.query(
        func.coalesce(
            func.sum(
                case(
                    (StockMovement.direction == "IN", StockMovement.quantity),
                    else_=-StockMovement.quantity,
                )
            ),
            0,
        )
    ).filter(StockMovement.product_id == product_id)
    if warehouse_id:
        query = query.filter(StockMovement.warehouse_id == warehouse_id)
    return query.scalar() or Decimal("0")


def get_stock_by_warehouse(db: Session, product_id: UUID) -> list[tuple[UUID, Decimal]]:
    rows = (
        db.query(
            StockMovement.warehouse_id,
            func.coalesce(
                func.sum(
                    case(
                        (StockMovement.direction == "IN", StockMovement.quantity),
                        else_=-StockMovement.quantity,
                    )
                ),
                0,
            ).label("qty"),
        )
        .filter(StockMovement.product_id == product_id)
        .group_by(StockMovement.warehouse_id)
        .all()
    )
    return [(row.warehouse_id, row.qty) for row in rows]


def create_movement(db: Session, data: StockMovementCreate) -> StockMovement:
    if data.direction == "OUT":
        total = get_product_stock(db, data.product_id)
        if total - data.quantity < 0:
            raise InsufficientStock
        wh_total = get_product_stock(db, data.product_id, data.warehouse_id)
        if wh_total - data.quantity < 0:
            raise InsufficientStock
    movement = StockMovement(**data.model_dump())
    db.add(movement)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(movement)
    return movement


def list_movements(
    db: Session,
    page: int,
    page_size: int,
    product_id: UUID | None = None,
    warehouse_id: UUID | None = None,
    direction: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> tuple[Sequence[StockMovement], int]:
    query = db.query(StockMovement)
    if product_id:
        query = query.filter(StockMovement.product_id == product_id)
    if warehouse_id:
        query = query.filter(StockMovement.warehouse_id == warehouse_id)
    if direction:
        query = query.filter(StockMovement.direction == direction)
    if date_from:
        query = query.filter(StockMovement.created_at_utc >= date_from)
    if date_to:
        query = query.filter(StockMovement.created_at_utc <= date_to)
    total = query.count()
    items = (
        query.order_by(StockMovement.created_at_utc.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def get_movement(db: Session, id: UUID) -> StockMovement | None:
    return db.get(StockMovement, id)


def delete_movement(db: Session, id: UUID) -> bool:
    movement = db.get(StockMovement, id)
    if not movement:
        return False
    db.delete(movement)
    db.commit()
    return True
