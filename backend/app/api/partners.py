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
from app.schemas.partner import (
    PartnerCreate,
    PartnerListResponse,
    PartnerPublic,
    PartnerUpdate,
)
from app.services.partner_service import (
    create_partner,
    delete_partner,
    get_partner,
    list_partners,
    update_partner,
)

router = APIRouter(prefix="/partners", tags=["partners"])


@router.get("", response_model=PartnerListResponse)
def list_partners_endpoint(
    pagination: tuple[int, int] = Depends(get_pagination),
    search: str | None = None,
    type: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    page, page_size = pagination
    items, total = list_partners(db, page, page_size, search, type)
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/{partner_id}", response_model=PartnerPublic)
def get_partner_endpoint(
    partner_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    partner = get_partner(db, partner_id)
    if not partner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partner not found")
    return partner


@router.post("", response_model=PartnerPublic, status_code=status.HTTP_201_CREATED)
def create_partner_endpoint(
    data: PartnerCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        partner = create_partner(db, data)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Partner with this tax number already exists",
        )
    return partner


@router.put("/{partner_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_partner_endpoint(
    partner_id: UUID,
    data: PartnerUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        partner = update_partner(db, partner_id, data)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Partner with this tax number already exists",
        )
    if not partner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partner not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{partner_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_partner_endpoint(
    partner_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    deleted = delete_partner(db, partner_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partner not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
