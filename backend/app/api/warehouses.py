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
from app.schemas.warehouse import (
    WarehouseCreate,
    WarehouseListResponse,
    WarehousePublic,
    WarehouseUpdate,
)
from app.services.warehouse_service import (
    create_warehouse,
    delete_warehouse,
    get_warehouse,
    list_warehouses,
    update_warehouse,
)

router = APIRouter(prefix="/warehouses", tags=["warehouses"])


@router.get("", response_model=WarehouseListResponse)
def list_warehouses_endpoint(
    pagination: tuple[int, int] = Depends(get_pagination),
    search: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    page, page_size = pagination
    items, total = list_warehouses(db, page, page_size, search)
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/{warehouse_id}", response_model=WarehousePublic)
def get_warehouse_endpoint(
    warehouse_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    warehouse = get_warehouse(db, warehouse_id)
    if not warehouse:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found")
    return warehouse


@router.post("", response_model=WarehousePublic, status_code=status.HTTP_201_CREATED)
def create_warehouse_endpoint(
    data: WarehouseCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        warehouse = create_warehouse(db, data)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Warehouse with this name or code already exists",
        )
    return warehouse


@router.put("/{warehouse_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_warehouse_endpoint(
    warehouse_id: UUID,
    data: WarehouseUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        warehouse = update_warehouse(db, warehouse_id, data)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Warehouse with this name or code already exists",
        )
    if not warehouse:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{warehouse_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_warehouse_endpoint(
    warehouse_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    deleted = delete_warehouse(db, warehouse_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
