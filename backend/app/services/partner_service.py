from typing import Sequence
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.partner import Partner
from app.schemas.partner import PartnerCreate, PartnerUpdate


def create_partner(db: Session, data: PartnerCreate) -> Partner:
    partner = Partner(**data.model_dump())
    db.add(partner)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(partner)
    return partner


def get_partner(db: Session, id: UUID) -> Partner | None:
    return db.get(Partner, id)


def list_partners(
    db: Session,
    page: int,
    page_size: int,
    search: str | None = None,
    type: str | None = None,
) -> tuple[Sequence[Partner], int]:
    query = db.query(Partner)
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
        query.order_by(Partner.created_at_utc.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def update_partner(db: Session, id: UUID, data: PartnerUpdate) -> Partner | None:
    partner = db.get(Partner, id)
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


def delete_partner(db: Session, id: UUID) -> bool:
    partner = db.get(Partner, id)
    if not partner:
        return False
    db.delete(partner)
    db.commit()
    return True
