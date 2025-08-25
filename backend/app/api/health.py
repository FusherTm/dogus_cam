from datetime import datetime, timedelta

from fastapi import APIRouter
from jose import jwt
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.db.session import SessionLocal

router = APIRouter()


@router.get("/health")
def health_check():
    db_status = "down"
    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
        db_status = "ok"
    except SQLAlchemyError:
        db_status = "down"

    auth_status = "down"
    try:
        jwt.encode(
            {"sub": "health", "exp": datetime.utcnow() + timedelta(minutes=1)},
            settings.SECRET_KEY,
            algorithm="HS256",
        )
        auth_status = "ready"
    except Exception:
        auth_status = "down"

    return {
        "status": "ok",
        "db": db_status,
        "version": settings.APP_VERSION,
        "auth": auth_status,
    }
