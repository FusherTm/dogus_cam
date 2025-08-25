from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.health import router as health_router
from app.api.users import router as users_router
from app.api.products import router as products_router
from app.api.categories import router as categories_router
from app.api.warehouses import router as warehouses_router
from app.api.stock_movements import router as stock_movements_router
from app.api.stock import router as stock_router
from app.api.partners import router as partners_router
from app.api.quotes import router as quotes_router
from app.api.sales_orders import router as sales_orders_router
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
app.include_router(products_router)
app.include_router(categories_router)
app.include_router(warehouses_router)
app.include_router(stock_movements_router)
app.include_router(stock_router)
app.include_router(partners_router)
app.include_router(quotes_router)
app.include_router(sales_orders_router)
