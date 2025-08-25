"""create partners table"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    if conn.dialect.name == "postgresql":
        op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')
        op.execute('CREATE EXTENSION IF NOT EXISTS "citext";')
    op.create_table(
        "partners",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("type", sa.Text(), nullable=False),
        sa.Column("email", postgresql.CITEXT(), nullable=True),
        sa.Column("phone", sa.Text(), nullable=True),
        sa.Column("tax_number", sa.Text(), nullable=True, unique=True),
        sa.Column("billing_address", sa.Text(), nullable=True),
        sa.Column("shipping_address", sa.Text(), nullable=True),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
        sa.Column(
            "created_at_utc",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "type IN ('customer','supplier','both')",
            name="chk_partner_type",
        ),
    )
    op.create_index(
        "ix_partners_name",
        "partners",
        [sa.text("lower(name)")],
    )
    op.create_index("ix_partners_type", "partners", ["type"])


def downgrade() -> None:
    op.drop_index("ix_partners_type", table_name="partners")
    op.drop_index("ix_partners_name", table_name="partners")
    op.drop_table("partners")
    conn = op.get_bind()
    if conn.dialect.name == "postgresql":
        op.execute('DROP EXTENSION IF EXISTS "citext";')
        op.execute('DROP EXTENSION IF EXISTS "pgcrypto";')
