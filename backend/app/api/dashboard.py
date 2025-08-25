from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.services.dashboard_service import (
    get_ar_summary,
    get_low_stock,
    get_sales_summary,
    get_top_customers,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def dashboard_summary(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return {
        "sales": get_sales_summary(db),
        "ar": get_ar_summary(db),
        "stock": {"low": get_low_stock(db)},
        "top_customers": get_top_customers(db),
    }

