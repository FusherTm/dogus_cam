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
from app.schemas.category import (
    CategoryCreate,
    CategoryListResponse,
    CategoryPublic,
    CategoryUpdate,
)
from app.services.category_service import (
    create_category,
    delete_category,
    get_category,
    list_categories,
    update_category,
)

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=CategoryListResponse)
def list_categories_endpoint(
    pagination: tuple[int, int] = Depends(get_pagination),
    search: str | None = None,
    db: Session = Depends(get_db),
    org: Organization = Depends(get_current_org),
    user: User = Depends(get_current_user_in_org),
):
    page, page_size = pagination
    items, total = list_categories(db, org.id, page, page_size, search)
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/{category_id}", response_model=CategoryPublic)
def get_category_endpoint(
    category_id: UUID,
    db: Session = Depends(get_db),
    org: Organization = Depends(get_current_org),
    user: User = Depends(get_current_user_in_org),
):
    category = get_category(db, org.id, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


@router.post("", response_model=CategoryPublic, status_code=status.HTTP_201_CREATED)
def create_category_endpoint(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
    org: Organization = Depends(get_current_org),
    _: User = Depends(get_current_user_in_org),
):
    try:
        category = create_category(db, org.id, data)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category with this name or code already exists",
        )
    return category


@router.put("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_category_endpoint(
    category_id: UUID,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
    org: Organization = Depends(get_current_org),
    _: User = Depends(get_current_user_in_org),
):
    try:
        category = update_category(db, org.id, category_id, data)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category with this name or code already exists",
        )
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category_endpoint(
    category_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
    org: Organization = Depends(get_current_org),
    _: User = Depends(get_current_user_in_org),
):
    deleted = delete_category(db, org.id, category_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
