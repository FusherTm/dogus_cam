from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import models to register with SQLAlchemy metadata
from app.models import (
    category,
    product,
    partner,
    order,
    user,
    organization,
    user_org,
)  # noqa: E402,F401
