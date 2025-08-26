from typing import Sequence
from uuid import UUID, uuid4

from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


def create_product(db: Session, org_id: UUID, data: ProductCreate) -> Product:
    product = Product(id=uuid4(), organization_id=org_id, **data.model_dump())
    db.add(product)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(product)
    return product


def get_product(db: Session, org_id: UUID, id: UUID) -> Product | None:
    return (
        db.query(Product)
        .filter(Product.id == id, Product.organization_id == org_id)
        .first()
    )


def list_products(
    db: Session,
    org_id: UUID,
    page: int,
    page_size: int,
    search: str | None = None,
) -> tuple[Sequence[Product], int]:
    query = db.query(Product).filter(Product.organization_id == org_id)
    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(Product.name.ilike(like), Product.sku.ilike(like))
        )
    total = query.count()
    items = (
        query.order_by(Product.name.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def update_product(db: Session, org_id: UUID, id: UUID, data: ProductUpdate) -> Product | None:
    product = (
        db.query(Product)
        .filter(Product.id == id, Product.organization_id == org_id)
        .first()
    )
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


def delete_product(db: Session, org_id: UUID, id: UUID) -> bool:
    product = (
        db.query(Product)
        .filter(Product.id == id, Product.organization_id == org_id)
        .first()
    )
    if not product:
        return False
    db.delete(product)
    db.commit()
    return True
