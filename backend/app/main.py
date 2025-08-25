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
from app.api.sales_invoices import router as sales_invoices_router
from app.api.ar import router as ar_router
from app.api.dashboard import router as dashboard_router
from app.api.employees import router as employees_router
from app.api.leaves import router as leaves_router
from app.core.security import hash_password
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user import User
from app.models.organization import Organization
from app.models.user_org import UserOrganization
from app.models.product import Product

app = FastAPI()


@app.on_event("startup")
def startup_event():
    with SessionLocal() as db:
        admin = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
        if not admin:
            admin = User(
                email=settings.ADMIN_EMAIL,
                password_hash=hash_password(settings.ADMIN_PASSWORD),
                role="admin",
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
        elif admin.role != "admin":
            admin.role = "admin"
            db.commit()

        org = db.query(Organization).filter(Organization.slug == "default").first()
        if not org:
            org = Organization(name="Default Org", slug="default")
            db.add(org)
            db.commit()
            db.refresh(org)

        membership = (
            db.query(UserOrganization)
            .filter(
                UserOrganization.user_id == admin.id,
                UserOrganization.org_id == org.id,
            )
            .first()
        )
        if not membership:
            db.add(
                UserOrganization(user_id=admin.id, org_id=org.id, role="owner")
            )
            db.commit()

        db.query(Product).filter(Product.org_id.is_(None)).update(
            {Product.org_id: org.id}, synchronize_session=False
        )
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
app.include_router(sales_invoices_router)
app.include_router(ar_router)
app.include_router(dashboard_router)
app.include_router(employees_router)
app.include_router(leaves_router)
