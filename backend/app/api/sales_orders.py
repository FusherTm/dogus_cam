from uuid import UUID
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.deps import (
    get_current_admin,
    get_current_user,
    get_db,
    get_pagination,
)
from app.models.user import User
from app.schemas.sales_order import (
    SalesOrderCreate,
    SalesOrderListResponse,
    SalesOrderPublic,
    SalesOrderUpdate,
)
from app.services.sales_order_service import (
    create_order,
    fulfill_order,
    get_order,
    list_orders,
    set_status,
    update_order,
)


class StatusChange(BaseModel):
    status: Literal["CONFIRMED", "FULFILLED", "CANCELLED"]


router = APIRouter(prefix="/sales/orders", tags=["sales-orders"])


@router.get("", response_model=SalesOrderListResponse)
def list_orders_endpoint(
    pagination: tuple[int, int] = Depends(get_pagination),
    search: str | None = None,
    status: str | None = None,
    partner_id: UUID | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    page, page_size = pagination
    items, total = list_orders(db, page, page_size, search, status, partner_id)
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/{order_id}", response_model=SalesOrderPublic)
def get_order_endpoint(
    order_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    order = get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


@router.post("", response_model=SalesOrderPublic, status_code=status.HTTP_201_CREATED)
def create_order_endpoint(
    data: SalesOrderCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    order = create_order(db, data)
    return order


@router.put("/{order_id}", response_model=SalesOrderPublic)
def update_order_endpoint(
    order_id: UUID,
    data: SalesOrderUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        order = update_order(db, order_id, data)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="immutable_state")
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


@router.post("/{order_id}/status", response_model=SalesOrderPublic)
def change_status_endpoint(
    order_id: UUID,
    body: StatusChange,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        if body.status == "FULFILLED":
            order = fulfill_order(db, order_id)
        else:
            order = set_status(db, order_id, body.status)
    except ValueError as e:
        detail = str(e)
        if detail == "insufficient_stock":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="insufficient_stock"
            )
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="invalid_status")
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order
