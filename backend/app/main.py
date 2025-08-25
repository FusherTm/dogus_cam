from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.health import router as health_router
from app.api.users import router as users_router
from app.core.security import hash_password
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user import User

app = FastAPI()


@app.on_event("startup")
def startup_event():
    with SessionLocal() as db:
        admin_exists = db.query(User).filter(User.role == "admin").first()
        if not admin_exists:
            admin = User(
                email=settings.ADMIN_EMAIL,
                password_hash=hash_password(settings.ADMIN_PASSWORD),
                role="admin",
            )
            db.add(admin)
            db.commit()


app.include_router(auth_router)
app.include_router(health_router)
app.include_router(users_router)
