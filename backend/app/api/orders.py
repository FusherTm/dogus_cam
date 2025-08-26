from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.deps import (
    get_current_admin,
    get_current_org,
    get_current_user_in_org,
    get_db,
    get_pagination,
)
from app.models.organization import Organization
from app.models.user import User
from app.schemas.order import (
    OrderCreate,
    OrderListResponse,
    OrderPublic,
    OrderUpdate,
)
from app.services.order_service import (
    create_order,
    delete_order,
    get_order,
    list_orders,
    update_order,
)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("", response_model=OrderListResponse)
def list_orders_endpoint(
    pagination: tuple[int, int] = Depends(get_pagination),
    db: Session = Depends(get_db),
    org: Organization = Depends(get_current_org),
    user: User = Depends(get_current_user_in_org),
):
    page, page_size = pagination
    items, total = list_orders(db, org.id, page, page_size)
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/{order_id}", response_model=OrderPublic)
def get_order_endpoint(
    order_id: UUID,
    db: Session = Depends(get_db),
    org: Organization = Depends(get_current_org),
    user: User = Depends(get_current_user_in_org),
):
    order = get_order(db, org.id, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


@router.post("", response_model=OrderPublic, status_code=status.HTTP_201_CREATED)
def create_order_endpoint(
    data: OrderCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
    org: Organization = Depends(get_current_org),
    _: User = Depends(get_current_user_in_org),
):
    try:
        order = create_order(db, org.id, data)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Order number conflict")
    return order


@router.put("/{order_id}", response_model=OrderPublic)
def update_order_endpoint(
    order_id: UUID,
    data: OrderUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
    org: Organization = Depends(get_current_org),
    _: User = Depends(get_current_user_in_org),
):
    try:
        order = update_order(db, org.id, order_id, data)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Order update conflict")
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order_endpoint(
    order_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
    org: Organization = Depends(get_current_org),
    _: User = Depends(get_current_user_in_org),
):
    deleted = delete_order(db, org.id, order_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
