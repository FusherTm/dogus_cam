import uuid
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column


class UUIDPKMixin:
    """Mixin providing a UUID primary key.

    Uses a Python-side default for SQLite tests while keeping the
    Postgres ``gen_random_uuid()`` server default for production.
    """

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )

