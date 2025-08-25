from typing import Sequence
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def create_category(db: Session, data: CategoryCreate) -> Category:
    category = Category(**data.model_dump())
    db.add(category)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(category)
    return category


def get_category(db: Session, id: UUID) -> Category | None:
    return db.get(Category, id)


def list_categories(
    db: Session, page: int, page_size: int, search: str | None = None
) -> tuple[Sequence[Category], int]:
    query = db.query(Category)
    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(Category.name.ilike(like), Category.code.ilike(like))
        )
    total = query.count()
    items = (
        query.order_by(Category.created_at_utc.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def update_category(db: Session, id: UUID, data: CategoryUpdate) -> Category | None:
    category = db.get(Category, id)
    if not category:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(category)
    return category


def delete_category(db: Session, id: UUID) -> bool:
    category = db.get(Category, id)
    if not category:
        return False
    db.delete(category)
    db.commit()
    return True
