from uuid import UUID
from typing import Sequence

from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.user import User


def list_users(db: Session, page: int, page_size: int, search: str | None = None) -> tuple[Sequence[User], int]:
    query = db.query(User)
    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(User.email.ilike(like), User.full_name.ilike(like))
        )
    total = query.count()
    items = (
        query.order_by(User.created_at_utc.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def get_user_by_id(db: Session, id: UUID) -> User | None:
    return db.get(User, id)
