import sys
from pathlib import Path
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.ext.compiler import compiles

sys.path.append(str(Path(__file__).resolve().parents[1]))

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("SECRET_KEY", "testsecret")
os.environ.setdefault("ADMIN_EMAIL", "admin@example.com")
os.environ.setdefault("ADMIN_PASSWORD", "password")

import app.main as app_main
from app.main import app
from app.db.base import Base
from app.core.deps import get_db
from app.db import session as db_session
from uuid import uuid4

from app.core.security import create_access_token, hash_password
from app.models.user import User


@compiles(CITEXT, "sqlite")
def compile_citext_sqlite(type_, compiler, **kw):
    return "TEXT"


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

db_session.engine = engine
db_session.SessionLocal = TestingSessionLocal


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
app_main.SessionLocal = TestingSessionLocal
app.router.on_startup.clear()


@pytest.fixture
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c


@pytest.fixture
def seed_users(client):
    db = TestingSessionLocal()
    admin = User(
        id=uuid4(),
        email="admin@example.com",
        password_hash=hash_password("secret"),
        role="admin",
        full_name="Admin User",
    )
    alice = User(
        id=uuid4(),
        email="alice@example.com",
        password_hash=hash_password("secret"),
        full_name="Alice Wonderland",
    )
    bob = User(
        id=uuid4(),
        email="bob@example.com",
        password_hash=hash_password("secret"),
        full_name="Bob Builder",
    )
    db.add_all([admin, alice, bob])
    db.commit()
    db.refresh(admin)
    db.refresh(alice)
    db.refresh(bob)
    db.close()
    return {"admin": admin, "alice": alice, "bob": bob}


@pytest.fixture
def admin_token(seed_users):
    return create_access_token(str(seed_users["admin"].id))


@pytest.fixture
def user_token(seed_users):
    return create_access_token(str(seed_users["alice"].id))
