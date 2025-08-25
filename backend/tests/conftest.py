import sys
from pathlib import Path
import os

import pytest
import httpx
import asyncio
from sqlalchemy import create_engine, event
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.dialects.postgresql import CITEXT, UUID
from sqlalchemy.ext.compiler import compiles

sys.path.append(str(Path(__file__).resolve().parents[1]))

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("SECRET_KEY", "testsecret")
os.environ.setdefault("ADMIN_EMAIL", "admin@example.com")
os.environ.setdefault("ADMIN_PASSWORD", "password")
os.environ.setdefault("APP_ENV", "test")

import app.main as app_main
from app.main import app
from app.db.base import Base
from app.core.deps import get_db
from app.db import session as db_session
from uuid import uuid4
import uuid

from app.core.security import create_access_token, hash_password
from app.models.user import User


@compiles(CITEXT, "sqlite")
def compile_citext_sqlite(type_, compiler, **kw):
    return "TEXT"


@compiles(UUID, "sqlite")
def compile_uuid_sqlite(type_, compiler, **kw):
    return "CHAR(36)"


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(engine, "connect")
def connect(dbapi_connection, connection_record):
    dbapi_connection.create_function("gen_random_uuid", 0, lambda: str(uuid.uuid4()))
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

db_session.engine = engine
db_session.SessionLocal = TestingSessionLocal

# Adjust server defaults for SQLite
for table in Base.metadata.tables.values():
    for col in table.columns:
        default = getattr(col.server_default, "arg", None)
        if default is not None and "gen_random_uuid" in str(default):
            col.server_default = sa.text("(gen_random_uuid())")


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
    class SyncClient:
        def __init__(self, app):
            self._transport = httpx.ASGITransport(app=app)
            self._client = httpx.AsyncClient(
                transport=self._transport, base_url="http://testserver"
            )

        def request(self, method, url, **kwargs):
            return asyncio.get_event_loop().run_until_complete(
                self._client.request(method, url, **kwargs)
            )

        def get(self, url, **kwargs):
            return self.request("GET", url, **kwargs)

        def post(self, url, **kwargs):
            return self.request("POST", url, **kwargs)

        def put(self, url, **kwargs):
            return self.request("PUT", url, **kwargs)

        def delete(self, url, **kwargs):
            return self.request("DELETE", url, **kwargs)

        def close(self):
            asyncio.get_event_loop().run_until_complete(self._client.aclose())

    client = SyncClient(app)
    try:
        yield client
    finally:
        client.close()


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
