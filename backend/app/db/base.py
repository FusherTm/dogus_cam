from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import models to register with SQLAlchemy metadata
from app.models import product, user  # noqa: E402,F401
