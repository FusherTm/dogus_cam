"""create warehouses and stock movements tables"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    if conn.dialect.name == "postgresql":
        op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')

    op.create_table(
        "warehouses",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("name", sa.Text(), nullable=False, unique=True),
        sa.Column("code", sa.Text(), nullable=True, unique=True),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
        sa.Column(
            "created_at_utc",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.create_table(
        "stock_movements",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "product_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("products.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "warehouse_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("warehouses.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "direction",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "quantity",
            sa.Numeric(14, 3),
            nullable=False,
        ),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("document_no", sa.Text(), nullable=True),
        sa.Column(
            "created_at_utc",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint("direction IN ('IN','OUT')", name="chk_direction"),
        sa.CheckConstraint("quantity > 0", name="chk_quantity_positive"),
    )

    op.create_index(
        "ix_stock_movements_prod",
        "stock_movements",
        ["product_id"],
    )
    op.create_index(
        "ix_stock_movements_wh",
        "stock_movements",
        ["warehouse_id"],
    )
    op.create_index(
        "ix_stock_movements_created",
        "stock_movements",
        [sa.text("created_at_utc DESC")],
    )


def downgrade() -> None:
    op.drop_index("ix_stock_movements_created", table_name="stock_movements")
    op.drop_index("ix_stock_movements_wh", table_name="stock_movements")
    op.drop_index("ix_stock_movements_prod", table_name="stock_movements")
    op.drop_table("stock_movements")
    op.drop_table("warehouses")
    conn = op.get_bind()
    if conn.dialect.name == "postgresql":
        op.execute('DROP EXTENSION IF EXISTS "pgcrypto";')
