from datetime import date
from decimal import Decimal
from typing import Sequence
from uuid import UUID

from sqlalchemy.orm import Session, selectinload

from app.models.sales_order import SalesOrder, SalesOrderItem
from app.models.warehouse import Warehouse
from app.schemas.sales_order import SalesOrderCreate, SalesOrderItemIn, SalesOrderUpdate
from app.schemas.stock_movement import StockMovementCreate
from app.services.stock_movement_service import (
    InsufficientStock,
    create_movement,
    get_product_stock,
)


def _generate_number(db: Session, order_date: date) -> str:
    year = order_date.year
    like = f"S-{year}-%"
    last = (
        db.query(SalesOrder.number)
        .filter(SalesOrder.number.like(like))
        .order_by(SalesOrder.number.desc())
        .first()
    )
    seq = int(last[0].split("-")[-1]) + 1 if last else 1
    return f"S-{year}-{seq:05d}"


def _calc_item(data: SalesOrderItemIn) -> SalesOrderItem:
    q = data.quantity
    price = data.unit_price
    disc = data.line_discount_rate / Decimal("100")
    tax_rate = data.tax_rate / Decimal("100")
    line_subtotal = q * price * (Decimal("1") - disc)
    line_tax = line_subtotal * tax_rate
    line_total = line_subtotal + line_tax
    return SalesOrderItem(
        product_id=data.product_id,
        description=data.description,
        quantity=q,
        unit_price=price,
        line_discount_rate=data.line_discount_rate,
        tax_rate=data.tax_rate,
        line_subtotal=line_subtotal,
        line_tax=line_tax,
        line_total=line_total,
    )


def _recalc_totals(order: SalesOrder) -> None:
    subtotal = sum((item.line_subtotal for item in order.items), Decimal("0"))
    tax_total = sum((item.line_tax for item in order.items), Decimal("0"))
    subtotal_after = subtotal * (Decimal("1") - order.discount_rate / Decimal("100"))
    order.subtotal = subtotal_after
    order.tax_total = tax_total
    order.grand_total = subtotal_after + tax_total


def create_order(db: Session, data: SalesOrderCreate) -> SalesOrder:
    order_date = data.order_date or date.today()
    number = _generate_number(db, order_date)
    order = SalesOrder(
        number=number,
        partner_id=data.partner_id,
        currency=data.currency,
        order_date=order_date,
        notes=data.notes,
        discount_rate=data.discount_rate,
    )
    for item_in in data.items:
        order.items.append(_calc_item(item_in))
    _recalc_totals(order)
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def get_order(db: Session, id: UUID) -> SalesOrder | None:
    return (
        db.query(SalesOrder)
        .options(selectinload(SalesOrder.items))
        .filter(SalesOrder.id == id)
        .first()
    )


def list_orders(
    db: Session,
    page: int,
    page_size: int,
    search: str | None = None,
    status: str | None = None,
    partner_id: UUID | None = None,
) -> tuple[Sequence[SalesOrder], int]:
    query = db.query(SalesOrder)
    if search:
        like = f"%{search}%"
        query = query.filter(SalesOrder.number.ilike(like))
    if status:
        query = query.filter(SalesOrder.status == status)
    if partner_id:
        query = query.filter(SalesOrder.partner_id == partner_id)
    total = query.count()
    items = (
        query.order_by(SalesOrder.created_at_utc.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def update_order(db: Session, id: UUID, data: SalesOrderUpdate) -> SalesOrder | None:
    order = db.query(SalesOrder).options(selectinload(SalesOrder.items)).get(id)
    if not order:
        return None
    if order.status != "NEW":
        raise ValueError("immutable_state")
    if data.notes is not None:
        order.notes = data.notes
    if data.discount_rate is not None:
        order.discount_rate = data.discount_rate
    if data.items is not None:
        order.items.clear()
        for item_in in data.items:
            order.items.append(_calc_item(item_in))
    _recalc_totals(order)
    db.commit()
    db.refresh(order)
    return order


def set_status(db: Session, id: UUID, new_status: str) -> SalesOrder | None:
    order = db.get(SalesOrder, id)
    if not order:
        return None
    transitions = {
        "NEW": {"CONFIRMED", "CANCELLED"},
        "CONFIRMED": {"FULFILLED", "CANCELLED"},
        "FULFILLED": set(),
        "CANCELLED": set(),
    }
    allowed = transitions.get(order.status, set())
    if new_status not in allowed:
        raise ValueError("invalid_status")
    order.status = new_status
    db.commit()
    db.refresh(order)
    return order


def fulfill_order(db: Session, id: UUID) -> SalesOrder | None:
    order = db.query(SalesOrder).options(selectinload(SalesOrder.items)).get(id)
    if not order:
        return None
    if order.status != "CONFIRMED":
        raise ValueError("invalid_status")
    warehouse = db.query(Warehouse).first()
    if not warehouse:
        raise ValueError("no_warehouse")
    try:
        for item in order.items:
            total = get_product_stock(db, item.product_id)
            wh_total = get_product_stock(db, item.product_id, warehouse.id)
            if total - item.quantity < 0 or wh_total - item.quantity < 0:
                raise InsufficientStock
        for item in order.items:
            movement = StockMovementCreate(
                product_id=item.product_id,
                warehouse_id=warehouse.id,
                direction="OUT",
                quantity=item.quantity,
                reason="sale",
                document_no=order.number,
            )
            create_movement(db, movement)
    except InsufficientStock:
        raise ValueError("insufficient_stock")
    order = set_status(db, id, "FULFILLED")
    return order
