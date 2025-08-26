from decimal import Decimal
from datetime import date
from sqlalchemy.orm import Session


def get_sales_summary(db: Session, today: date | None = None) -> dict:
    return {"today": Decimal("0"), "month": Decimal("0")}


def get_ar_summary(db: Session) -> dict:
    return {
        "open_total": Decimal("0"),
        "aging": {"0_30": Decimal("0"), "31_60": Decimal("0"), "61_90": Decimal("0"), "90_plus": Decimal("0")},
    }


def get_low_stock(db: Session) -> list[dict]:
    return []


def get_top_customers(db: Session, limit: int = 5) -> list[dict]:
    return []
