from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import (
    get_current_admin,
    get_current_user,
    get_db,
    get_pagination,
)
from app.models.user import User
from app.schemas.user import UserListResponse, UserPublic
from app.services.user_service import get_user_by_id, list_users

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserPublic)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("", response_model=UserListResponse)
def admin_list_users(
    pagination: tuple[int, int] = Depends(get_pagination),
    search: str | None = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    page, page_size = pagination
    items, total = list_users(db, page, page_size, search)
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/{user_id}", response_model=UserPublic)
def admin_get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
