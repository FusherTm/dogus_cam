"""add organizations"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0014"
down_revision = "0013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("slug", sa.Text(), nullable=False, unique=True),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "user_organizations",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.Text(), nullable=False, server_default=sa.text("'owner'")),
        sa.PrimaryKeyConstraint("user_id", "org_id"),
        sa.CheckConstraint("role IN ('owner','member')", name="ck_user_organizations_role"),
    )

    op.execute(
        "ALTER TABLE products ADD COLUMN IF NOT EXISTS org_id UUID NULL REFERENCES organizations(id) ON DELETE RESTRICT"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_products_org ON products(org_id, created_at_utc DESC)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_products_org")
    op.execute("ALTER TABLE products DROP COLUMN IF EXISTS org_id")
    op.drop_table("user_organizations")
    op.drop_table("organizations")
