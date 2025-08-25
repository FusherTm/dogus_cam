from typing import Sequence
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


def create_product(db: Session, data: ProductCreate) -> Product:
    product = Product(**data.model_dump())
    db.add(product)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(product)
    return product


def get_product(db: Session, id: UUID) -> Product | None:
    return db.get(Product, id)


def list_products(
    db: Session, page: int, page_size: int, search: str | None = None
) -> tuple[Sequence[Product], int]:
    query = db.query(Product)
    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(Product.name.ilike(like), Product.sku.ilike(like))
        )
    total = query.count()
    items = (
        query.order_by(Product.created_at_utc.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def update_product(db: Session, id: UUID, data: ProductUpdate) -> Product | None:
    product = db.get(Product, id)
    if not product:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(product)
    return product


def delete_product(db: Session, id: UUID) -> bool:
    product = db.get(Product, id)
    if not product:
        return False
    db.delete(product)
    db.commit()
    return True
