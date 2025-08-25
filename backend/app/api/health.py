from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import SessionLocal
from app.core.config import settings

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
    return {"status": "ok", "db": db_status, "version": settings.APP_VERSION}
