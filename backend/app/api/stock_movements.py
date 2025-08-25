from datetime import datetime
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.deps import (
    get_current_admin,
    get_current_user,
    get_db,
    get_pagination,
)
from app.models.user import User
from app.schemas.stock_movement import (
    StockMovementCreate,
    StockMovementListResponse,
    StockMovementPublic,
)
from app.services.stock_movement_service import (
    InsufficientStock,
    create_movement,
    delete_movement,
    get_movement,
    list_movements,
)

router = APIRouter(prefix="/stock-movements", tags=["stock-movements"])


@router.get("", response_model=StockMovementListResponse)
def list_movements_endpoint(
    pagination: tuple[int, int] = Depends(get_pagination),
    product_id: UUID | None = None,
    warehouse_id: UUID | None = None,
    direction: Literal["IN", "OUT"] | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    page, page_size = pagination
    items, total = list_movements(
        db,
        page,
        page_size,
        product_id=product_id,
        warehouse_id=warehouse_id,
        direction=direction,
        date_from=date_from,
        date_to=date_to,
    )
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/{movement_id}", response_model=StockMovementPublic)
def get_movement_endpoint(
    movement_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    movement = get_movement(db, movement_id)
    if not movement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock movement not found")
    return movement


@router.post("", response_model=StockMovementPublic, status_code=status.HTTP_201_CREATED)
def create_movement_endpoint(
    data: StockMovementCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        movement = create_movement(db, data)
    except InsufficientStock:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="insufficient_stock")
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid product or warehouse",
        )
    return movement


@router.delete("/{movement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movement_endpoint(
    movement_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    deleted = delete_movement(db, movement_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock movement not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
