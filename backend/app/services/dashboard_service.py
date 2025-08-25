from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.sales_invoice import SalesInvoice
from app.models.ar import ARAllocation, AREntry
from app.models.partner import Partner
from app.models.stock_movement import StockMovement


def get_sales_summary(db: Session, today: date | None = None) -> dict:
    today = today or date.today()
    month_start = today.replace(day=1)
    next_month = (month_start + timedelta(days=32)).replace(day=1)

    today_total = (
        db.query(func.coalesce(func.sum(SalesInvoice.grand_total), 0))
        .filter(
            SalesInvoice.status.in_(["ISSUED", "PAID"]),
            SalesInvoice.issue_date == today,
        )
        .scalar()
        or Decimal("0")
    )
    month_total = (
        db.query(func.coalesce(func.sum(SalesInvoice.grand_total), 0))
        .filter(
            SalesInvoice.status.in_(["ISSUED", "PAID"]),
            SalesInvoice.issue_date >= month_start,
            SalesInvoice.issue_date < next_month,
        )
        .scalar()
        or Decimal("0")
    )
    return {"today": today_total, "month": month_total}


def get_ar_summary(db: Session) -> dict:
    invoices = (
        db.query(SalesInvoice)
        .filter(SalesInvoice.status != "CANCELLED")
        .all()
    )
    alloc_rows = (
        db.query(
            ARAllocation.invoice_id,
            func.coalesce(
                func.sum(
                    case(
                        (AREntry.type.in_(["PAYMENT", "ADJUSTMENT"]), ARAllocation.amount),
                        (AREntry.type == "REFUND", -ARAllocation.amount),
                        else_=0,
                    )
                ),
                0,
            ).label("allocated"),
        )
        .join(AREntry)
        .group_by(ARAllocation.invoice_id)
        .all()
    )
    alloc_map = {row.invoice_id: Decimal(row.allocated) for row in alloc_rows}

    open_total = Decimal("0")
    bucket_0_30 = Decimal("0")
    bucket_31_60 = Decimal("0")
    bucket_61_90 = Decimal("0")
    bucket_90_plus = Decimal("0")
    today = date.today()
    for inv in invoices:
        allocated = alloc_map.get(inv.id, Decimal("0"))
        remaining = inv.grand_total - allocated
        if remaining <= 0:
            continue
        open_total += remaining
        if inv.status == "ISSUED":
            age = (today - inv.issue_date).days
            if age <= 30:
                bucket_0_30 += remaining
            elif age <= 60:
                bucket_31_60 += remaining
            elif age <= 90:
                bucket_61_90 += remaining
            else:
                bucket_90_plus += remaining
    return {
        "open_total": open_total,
        "aging": {
            "0_30": bucket_0_30,
            "31_60": bucket_31_60,
            "61_90": bucket_61_90,
            "90_plus": bucket_90_plus,
        },
    }


def get_low_stock(db: Session) -> list[dict]:
    qty_sub = (
        db.query(
            StockMovement.product_id,
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
        .group_by(StockMovement.product_id)
        .subquery()
    )
    rows = (
        db.query(
            Product.id.label("product_id"),
            Product.sku,
            Product.name,
            func.coalesce(qty_sub.c.qty, 0).label("total"),
            Product.restock_level,
        )
        .outerjoin(qty_sub, Product.id == qty_sub.c.product_id)
        .filter(
            Product.restock_level > 0,
            func.coalesce(qty_sub.c.qty, 0) < Product.restock_level,
        )
        .all()
    )
    return [
        {
            "product_id": r.product_id,
            "sku": r.sku,
            "name": r.name,
            "total": r.total,
            "restock_level": r.restock_level,
        }
        for r in rows
    ]


def get_top_customers(db: Session, limit: int = 5) -> list[dict]:
    cutoff = date.today() - timedelta(days=90)
    rows = (
        db.query(
            SalesInvoice.partner_id,
            Partner.name,
            func.sum(SalesInvoice.grand_total).label("total"),
        )
        .join(Partner, Partner.id == SalesInvoice.partner_id)
        .filter(
            SalesInvoice.status.in_(["ISSUED", "PAID"]),
            SalesInvoice.issue_date >= cutoff,
        )
        .group_by(SalesInvoice.partner_id, Partner.name)
        .order_by(func.sum(SalesInvoice.grand_total).desc())
        .limit(limit)
        .all()
    )
    return [
        {"partner_id": r.partner_id, "name": r.name, "total": r.total}
        for r in rows
    ]
