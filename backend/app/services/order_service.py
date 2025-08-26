from datetime import datetime
from decimal import Decimal
from typing import Sequence
from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.order import Order, OrderItem
from app.models.production_job import ProductionJob
from app.models.user import User
from app.schemas.order import OrderCreate, OrderUpdate


def create_order(db: Session, org_id: UUID, data: OrderCreate) -> Order:
    year = datetime.utcnow().year
    last_order = db.query(Order).order_by(Order.number.desc()).first()
    if last_order and last_order.number.startswith(f"{year}-"):
        seq = int(last_order.number.split("-")[1]) + 1
    else:
        seq = 1
    order_number = f"{year}-{seq:03d}"

    items = []
    grand_total = Decimal("0")
    for item in data.items:
        total_price = (
            (item.width / Decimal("1000"))
            * (item.height / Decimal("1000"))
            * item.quantity
            * item.unit_price
        )
        order_item = OrderItem(
            id=uuid4(),
            product_id=item.product_id,
            description=item.description,
            quantity=item.quantity,
            unit_price=item.unit_price,
            width=item.width,
            height=item.height,
            line_discount_rate=item.line_discount_rate,
            tax_rate=item.tax_rate,
            line_subtotal=total_price,
            line_tax=Decimal("0"),
            line_total=total_price,
        )
        items.append(order_item)
        grand_total += total_price

    order = Order(
        id=uuid4(),
        organization_id=org_id,
        number=order_number,
        partner_id=data.partner_id,
        project_name=data.project_name,
        delivery_date=data.delivery_date,
        status="TEKLIF",
        discount_rate=data.discount_rate,
        notes=data.notes,
        subtotal=grand_total,
        tax_total=Decimal("0"),
        grand_total=grand_total,
        items=items,
    )
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
    db: Session, org_id: UUID, page: int, page_size: int
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
        order.items = [
            OrderItem(
                id=uuid4(),
                product_id=item.product_id,
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                width=item.width,
                height=item.height,
                line_discount_rate=item.line_discount_rate,
                tax_rate=item.tax_rate,
            )
            for item in data.items
        ]
    grand_total = Decimal("0")
    for item in order.items:
        total_price = (
            (item.width / Decimal("1000"))
            * (item.height / Decimal("1000"))
            * item.quantity
            * item.unit_price
        )
        item.line_subtotal = total_price
        item.line_tax = Decimal("0")
        item.line_total = total_price
        grand_total += total_price
    order.subtotal = grand_total
    order.tax_total = Decimal("0")
    order.grand_total = grand_total

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


def update_order_status(db: Session, id: UUID, new_status: str, current_user: User) -> Order | None:
    order = db.query(Order).filter(Order.id == id).first()
    if not order:
        return None
    order.status = new_status
    if new_status == "URETIMDE":
        for item in order.items:
            job = ProductionJob(
                id=uuid4(),
                order_item_id=item.id,
                quantity_required=item.quantity,
            )
            db.add(job)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(order)
    return order
