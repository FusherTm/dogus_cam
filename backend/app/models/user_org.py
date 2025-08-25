from sqlalchemy import CheckConstraint, Column, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.schema import ForeignKey

from app.db.base import Base


class UserOrganization(Base):
    __tablename__ = "user_organizations"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    org_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    role = Column(Text, nullable=False, server_default=text("'owner'"))

    __table_args__ = (
        CheckConstraint("role IN ('owner','member')", name="ck_user_organizations_role"),
    )
