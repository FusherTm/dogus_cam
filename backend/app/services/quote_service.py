from datetime import date
from decimal import Decimal
from typing import Sequence
from uuid import UUID

from sqlalchemy.orm import Session, selectinload

from app.models.quote import Quote, QuoteItem
from app.models.sales_order import SalesOrder
from app.schemas.quote import QuoteCreate, QuoteUpdate, QuoteItemIn
from app.schemas.sales_order import SalesOrderCreate, SalesOrderItemIn
from app.services.sales_order_service import create_order


def _generate_number(db: Session, issue_date: date) -> str:
    year = issue_date.year
    like = f"Q-{year}-%"
    last = (
        db.query(Quote.number)
        .filter(Quote.number.like(like))
        .order_by(Quote.number.desc())
        .first()
    )
    if last:
        seq = int(last[0].split("-")[-1]) + 1
    else:
        seq = 1
    return f"Q-{year}-{seq:05d}"


def _calc_item(data: QuoteItemIn) -> QuoteItem:
    q = data.quantity
    price = data.unit_price
    disc = data.line_discount_rate / Decimal("100")
    tax_rate = data.tax_rate / Decimal("100")
    line_subtotal = q * price * (Decimal("1") - disc)
    line_tax = line_subtotal * tax_rate
    line_total = line_subtotal + line_tax
    return QuoteItem(
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


def _recalc_totals(quote: Quote) -> None:
    subtotal = sum((item.line_subtotal for item in quote.items), Decimal("0"))
    tax_total = sum((item.line_tax for item in quote.items), Decimal("0"))
    subtotal_after = subtotal * (Decimal("1") - quote.discount_rate / Decimal("100"))
    quote.subtotal = subtotal_after
    quote.tax_total = tax_total
    quote.grand_total = subtotal_after + tax_total


def create_quote(db: Session, data: QuoteCreate) -> Quote:
    issue_date = data.issue_date or date.today()
    number = _generate_number(db, issue_date)
    quote = Quote(
        number=number,
        partner_id=data.partner_id,
        currency=data.currency,
        issue_date=issue_date,
        valid_until=data.valid_until,
        notes=data.notes,
        discount_rate=data.discount_rate,
    )
    for item_in in data.items:
        quote.items.append(_calc_item(item_in))
    _recalc_totals(quote)
    db.add(quote)
    db.commit()
    db.refresh(quote)
    return quote


def get_quote(db: Session, id: UUID) -> Quote | None:
    return (
        db.query(Quote)
        .options(selectinload(Quote.items))
        .filter(Quote.id == id)
        .first()
    )


def list_quotes(
    db: Session,
    page: int,
    page_size: int,
    search: str | None = None,
    status: str | None = None,
    partner_id: UUID | None = None,
) -> tuple[Sequence[Quote], int]:
    query = db.query(Quote)
    if search:
        like = f"%{search}%"
        query = query.filter(Quote.number.ilike(like))
    if status:
        query = query.filter(Quote.status == status)
    if partner_id:
        query = query.filter(Quote.partner_id == partner_id)
    total = query.count()
    items = (
        query.order_by(Quote.created_at_utc.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def update_quote(db: Session, id: UUID, data: QuoteUpdate) -> Quote | None:
    quote = db.query(Quote).options(selectinload(Quote.items)).get(id)
    if not quote:
        return None
    if quote.status != "DRAFT":
        raise ValueError("immutable_state")
    if data.notes is not None:
        quote.notes = data.notes
    if data.discount_rate is not None:
        quote.discount_rate = data.discount_rate
    if data.valid_until is not None:
        quote.valid_until = data.valid_until
    if data.items is not None:
        quote.items.clear()
        for item_in in data.items:
            quote.items.append(_calc_item(item_in))
    _recalc_totals(quote)
    db.commit()
    db.refresh(quote)
    return quote


def set_status(db: Session, id: UUID, new_status: str) -> Quote | None:
    quote = db.get(Quote, id)
    if not quote:
        return None
    transitions = {
        "DRAFT": {"SENT", "APPROVED", "REJECTED"},
        "SENT": {"APPROVED", "REJECTED", "EXPIRED"},
        "APPROVED": set(),
        "REJECTED": set(),
        "EXPIRED": set(),
    }
    allowed = transitions.get(quote.status, set())
    if new_status not in allowed:
        raise ValueError("invalid_status")
    quote.status = new_status
    db.commit()
    db.refresh(quote)
    return quote


def convert_quote_to_order(db: Session, quote_id: UUID) -> SalesOrder | None:
    quote = db.query(Quote).options(selectinload(Quote.items)).get(quote_id)
    if not quote:
        return None
    if quote.status not in {"APPROVED", "SENT"}:
        raise ValueError("invalid_status")
    order_data = SalesOrderCreate(
        partner_id=quote.partner_id,
        currency=quote.currency,
        order_date=date.today(),
        notes=quote.notes,
        discount_rate=quote.discount_rate,
        items=[
            SalesOrderItemIn(
                product_id=item.product_id,
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                line_discount_rate=item.line_discount_rate,
                tax_rate=item.tax_rate,
            )
            for item in quote.items
        ],
    )
    order = create_order(db, order_data)
    return order
