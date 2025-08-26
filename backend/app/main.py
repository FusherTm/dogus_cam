from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.health import router as health_router
from app.api.users import router as users_router
from app.api.products import router as products_router
from app.api.categories import router as categories_router
from app.api.partners import router as partners_router
from app.api.orders import router as orders_router
from app.api.dashboard import router as dashboard_router
from app.api.finance import router as finance_router
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

        db.query(Product).filter(Product.organization_id.is_(None)).update(
            {Product.organization_id: org.id}, synchronize_session=False
        )
        db.commit()


app.include_router(auth_router)
app.include_router(health_router)
app.include_router(users_router)
app.include_router(products_router)
app.include_router(categories_router)
app.include_router(partners_router)
app.include_router(orders_router)
app.include_router(dashboard_router)
app.include_router(finance_router)
