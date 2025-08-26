from typing import Sequence
from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.order import Order, OrderItem
from app.schemas.order import OrderCreate, OrderUpdate


def _calculate_totals(order: Order) -> None:
    subtotal = 0
    tax_total = 0
    for item in order.items:
        line_subtotal = item.quantity * item.unit_price * (1 - item.line_discount_rate / 100)
        line_tax = line_subtotal * (item.tax_rate / 100)
        item.line_subtotal = line_subtotal
        item.line_tax = line_tax
        item.line_total = line_subtotal + line_tax
        subtotal += line_subtotal
        tax_total += line_tax
    order.subtotal = subtotal
    order.tax_total = tax_total
    order.grand_total = subtotal + tax_total


def create_order(db: Session, org_id: UUID, data: OrderCreate) -> Order:
    order = Order(
        id=uuid4(),
        organization_id=org_id,
        number=f"ORD-{uuid4().hex[:8].upper()}",
        partner_id=data.partner_id,
        project_name=data.project_name,
        delivery_date=data.delivery_date,
        status=data.status or "TEKLIF",
        discount_rate=data.discount_rate,
        notes=data.notes,
        items=[OrderItem(**item.model_dump()) for item in data.items],
    )
    _calculate_totals(order)
    db.add(order)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(order)
    return order


def get_order(db: Session, org_id: UUID, id: UUID) -> Order | None:
    return (
        db.query(Order)
        .filter(Order.id == id, Order.organization_id == org_id)
        .first()
    )


def list_orders(
    db: Session,
    org_id: UUID,
    page: int,
    page_size: int,
) -> tuple[Sequence[Order], int]:
    query = db.query(Order).filter(Order.organization_id == org_id)
    total = query.count()
    items = (
        query.order_by(Order.created_at_utc.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def update_order(db: Session, org_id: UUID, id: UUID, data: OrderUpdate) -> Order | None:
    order = (
        db.query(Order)
        .filter(Order.id == id, Order.organization_id == org_id)
        .first()
    )
    if not order:
        return None
    for field, value in data.model_dump(exclude_unset=True, exclude={"items"}).items():
        setattr(order, field, value)
    if data.items is not None:
        order.items = [OrderItem(**item.model_dump()) for item in data.items]
    _calculate_totals(order)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(order)
    return order


def delete_order(db: Session, org_id: UUID, id: UUID) -> bool:
    order = (
        db.query(Order)
        .filter(Order.id == id, Order.organization_id == org_id)
        .first()
    )
    if not order:
        return False
    db.delete(order)
    db.commit()
    return True
