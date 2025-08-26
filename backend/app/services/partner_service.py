from typing import Sequence
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.partner import Partner
from app.schemas.partner import PartnerCreate, PartnerUpdate


def create_partner(db: Session, org_id: UUID, data: PartnerCreate) -> Partner:
    partner = Partner(organization_id=org_id, **data.model_dump())
    db.add(partner)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(partner)
    return partner


def get_partner(db: Session, org_id: UUID, id: UUID) -> Partner | None:
    return (
        db.query(Partner)
        .filter(Partner.id == id, Partner.organization_id == org_id)
        .first()
    )


def list_partners(
    db: Session,
    org_id: UUID,
    page: int,
    page_size: int,
    search: str | None = None,
    type: str | None = None,
) -> tuple[Sequence[Partner], int]:
    query = db.query(Partner).filter(Partner.organization_id == org_id)
    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(
                Partner.name.ilike(like),
                Partner.email.ilike(like),
                Partner.phone.ilike(like),
            )
        )
    if type:
        query = query.filter(Partner.type == type)
    total = query.count()
    items = (
        query.order_by(Partner.name.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def update_partner(db: Session, org_id: UUID, id: UUID, data: PartnerUpdate) -> Partner | None:
    partner = (
        db.query(Partner)
        .filter(Partner.id == id, Partner.organization_id == org_id)
        .first()
    )
    if not partner:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(partner, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(partner)
    return partner


def delete_partner(db: Session, org_id: UUID, id: UUID) -> bool:
    partner = (
        db.query(Partner)
        .filter(Partner.id == id, Partner.organization_id == org_id)
        .first()
    )
    if not partner:
        return False
    db.delete(partner)
    db.commit()
    return True
