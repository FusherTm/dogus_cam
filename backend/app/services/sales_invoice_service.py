from datetime import date
from decimal import Decimal
from typing import Sequence
from uuid import UUID

from sqlalchemy.orm import Session, selectinload

from app.models.sales_invoice import SalesInvoice, SalesInvoiceItem
from app.models.sales_order import SalesOrder
from app.models.ar import ARAllocation
from app.schemas.sales_invoice import (
    SalesInvoiceCreate,
    SalesInvoiceItemIn,
    SalesInvoiceUpdate,
)
from app.services.ar_service import compute_partner_balance, on_invoice_issued


def _generate_number(db: Session, issue_date: date) -> str:
    year = issue_date.year
    like = f"I-{year}-%"
    last = (
        db.query(SalesInvoice.number)
        .filter(SalesInvoice.number.like(like))
        .order_by(SalesInvoice.number.desc())
        .first()
    )
    seq = int(last[0].split("-")[-1]) + 1 if last else 1
    return f"I-{year}-{seq:05d}"


def _calc_item(data: SalesInvoiceItemIn) -> SalesInvoiceItem:
    q = data.quantity
    price = data.unit_price
    disc = data.line_discount_rate / Decimal("100")
    tax_rate = data.tax_rate / Decimal("100")
    line_subtotal = q * price * (Decimal("1") - disc)
    line_tax = line_subtotal * tax_rate
    line_total = line_subtotal + line_tax
    return SalesInvoiceItem(
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


def _recalc_totals(invoice: SalesInvoice) -> None:
    subtotal = sum((item.line_subtotal for item in invoice.items), Decimal("0"))
    tax_total = sum((item.line_tax for item in invoice.items), Decimal("0"))
    subtotal_after = subtotal * (Decimal("1") - invoice.discount_rate / Decimal("100"))
    invoice.subtotal = subtotal_after
    invoice.tax_total = tax_total
    invoice.grand_total = subtotal_after + tax_total


def create_invoice(db: Session, data: SalesInvoiceCreate) -> SalesInvoice:
    issue_date = data.issue_date or date.today()
    number = _generate_number(db, issue_date)
    if data.order_id:
        order = db.get(SalesOrder, data.order_id)
        if not order:
            raise ValueError("order_not_found")
        if order.partner_id != data.partner_id:
            raise ValueError("partner_mismatch")
    invoice = SalesInvoice(
        number=number,
        partner_id=data.partner_id,
        order_id=data.order_id,
        currency=data.currency,
        issue_date=issue_date,
        notes=data.notes,
        discount_rate=data.discount_rate,
    )
    for item_in in data.items:
        invoice.items.append(_calc_item(item_in))
    _recalc_totals(invoice)
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


def get_invoice(db: Session, id: UUID) -> SalesInvoice | None:
    return (
        db.query(SalesInvoice)
        .options(selectinload(SalesInvoice.items))
        .filter(SalesInvoice.id == id)
        .first()
    )


def list_invoices(
    db: Session,
    page: int,
    page_size: int,
    search: str | None = None,
    status: str | None = None,
    partner_id: UUID | None = None,
) -> tuple[Sequence[SalesInvoice], int]:
    query = db.query(SalesInvoice)
    if search:
        like = f"%{search}%"
        query = query.filter(SalesInvoice.number.ilike(like))
    if status:
        query = query.filter(SalesInvoice.status == status)
    if partner_id:
        query = query.filter(SalesInvoice.partner_id == partner_id)
    total = query.count()
    items = (
        query.order_by(SalesInvoice.created_at_utc.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def update_invoice(
    db: Session, id: UUID, data: SalesInvoiceUpdate
) -> SalesInvoice | None:
    invoice = db.query(SalesInvoice).options(selectinload(SalesInvoice.items)).get(id)
    if not invoice:
        return None
    if invoice.status != "DRAFT":
        raise ValueError("immutable_state")
    if data.notes is not None:
        invoice.notes = data.notes
    if data.discount_rate is not None:
        invoice.discount_rate = data.discount_rate
    if data.items is not None:
        invoice.items.clear()
        for item_in in data.items:
            invoice.items.append(_calc_item(item_in))
    _recalc_totals(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


def set_status(db: Session, id: UUID, new_status: str) -> SalesInvoice | None:
    invoice = db.get(SalesInvoice, id)
    if not invoice:
        return None
    transitions = {
        "DRAFT": {"ISSUED", "CANCELLED"},
        "ISSUED": {"PAID", "CANCELLED"},
        "PAID": set(),
        "CANCELLED": set(),
    }
    allowed = transitions.get(invoice.status, set())
    if new_status not in allowed:
        raise ValueError("invalid_status")
    if invoice.status == "DRAFT" and new_status == "ISSUED":
        invoice.status = new_status
        db.commit()
        db.refresh(invoice)
        on_invoice_issued(db, invoice)
        return invoice
    if invoice.status == "ISSUED" and new_status == "PAID":
        balance = compute_partner_balance(db, invoice.partner_id)
        inv_bal = next(
            (b for b in balance["by_invoice"] if b["invoice_id"] == invoice.id),
            None,
        )
        if not inv_bal or inv_bal["remaining"] != Decimal("0"):
            raise ValueError("unsettled_balance")
        invoice.status = new_status
        db.commit()
        db.refresh(invoice)
        return invoice
    if new_status == "CANCELLED":
        alloc_exists = (
            db.query(ARAllocation)
            .filter(ARAllocation.invoice_id == invoice.id)
            .first()
        )
        if alloc_exists:
            raise ValueError("allocated_invoice")
        invoice.status = new_status
        db.commit()
        db.refresh(invoice)
        return invoice
    invoice.status = new_status
    db.commit()
    db.refresh(invoice)
    return invoice
