"""add restock_level to products"""

from alembic import op
import sqlalchemy as sa

revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "products",
        sa.Column("restock_level", sa.Numeric(14, 3), nullable=False, server_default=sa.text("0")),
    )


def downgrade() -> None:
    op.drop_column("products", "restock_level")

