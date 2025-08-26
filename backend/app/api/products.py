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
from app.schemas.product import (
    ProductCreate,
    ProductListResponse,
    ProductPublic,
    ProductUpdate,
)
from app.services.product_service import (
    create_product,
    delete_product,
    get_product,
    list_products,
    update_product,
)

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=ProductListResponse)
def list_products_endpoint(
    pagination: tuple[int, int] = Depends(get_pagination),
    search: str | None = None,
    db: Session = Depends(get_db),
    org: Organization = Depends(get_current_org),
    user: User = Depends(get_current_user_in_org),
):
    page, page_size = pagination
    items, total = list_products(db, org.id, page, page_size, search)
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/{product_id}", response_model=ProductPublic)
def get_product_endpoint(
    product_id: UUID,
    db: Session = Depends(get_db),
    org: Organization = Depends(get_current_org),
    user: User = Depends(get_current_user_in_org),
):
    product = get_product(db, org.id, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.post("", response_model=ProductPublic, status_code=status.HTTP_201_CREATED)
def create_product_endpoint(
    data: ProductCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
    org: Organization = Depends(get_current_org),
    _: User = Depends(get_current_user_in_org),
):
    if data.base_price_sqm < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Price must be non-negative")
    try:
        product = create_product(db, org.id, data)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="SKU already exists")
    return product


@router.put("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_product_endpoint(
    product_id: UUID,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
    org: Organization = Depends(get_current_org),
    _: User = Depends(get_current_user_in_org),
):
    if data.base_price_sqm is not None and data.base_price_sqm < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Price must be non-negative")
    try:
        product = update_product(db, org.id, product_id, data)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="SKU already exists")
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_endpoint(
    product_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
    org: Organization = Depends(get_current_org),
    _: User = Depends(get_current_user_in_org),
):
    deleted = delete_product(db, org.id, product_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
