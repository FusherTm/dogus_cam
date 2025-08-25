from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import models to register with SQLAlchemy metadata
from app.models import (
    category,
    product,
    stock_movement,
    user,
    warehouse,
    partner,
    quote,
    sales_order,
    sales_invoice,
    ar,
    employee,
    leave_type,
    leave_request,
)  # noqa: E402,F401
