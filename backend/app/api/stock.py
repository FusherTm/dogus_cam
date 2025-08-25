from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.product import Product
from app.models.user import User
from app.services.stock_movement_service import (
    get_product_stock,
    get_stock_by_warehouse,
)

router = APIRouter(prefix="/stock", tags=["stock"])


@router.get("/product/{product_id}")
def get_product_stock_endpoint(
    product_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    total = get_product_stock(db, product_id)
    by_wh = [
        {"warehouse_id": wid, "qty": qty}
        for wid, qty in get_stock_by_warehouse(db, product_id)
    ]
    return {"product_id": product_id, "total": total, "by_warehouse": by_wh}
