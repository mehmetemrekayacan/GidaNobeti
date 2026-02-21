"""Add food_content column to orders table

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2026-02-19

Sipariş içeriği (yenen yemekler) özetini saklayan TEXT sütunu.
Örnek: "1x Pizza X-Large, 1x Cheddar Sos"
Gıda zehirlenmesi analizlerinde hangi yemeğin yendiğini hızlıca
görmek için kullanılır.
"""
from alembic import op
import sqlalchemy as sa

revision = "b2c3d4e5f6g7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "orders",
        sa.Column("food_content", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("orders", "food_content")
