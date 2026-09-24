"""Create the cart items table.

Revision ID: a6f2c9e7b481
Revises: bdfcecb9fac6
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a6f2c9e7b481"
down_revision = "bdfcecb9fac6"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "cart_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "product_id",
            name="uq_cart_items_user_product",
        ),
    )
    op.create_index(
        op.f("ix_cart_items_user_id"),
        "cart_items",
        ["user_id"],
        unique=False,
    )


def downgrade():
    op.drop_index(op.f("ix_cart_items_user_id"), table_name="cart_items")
    op.drop_table("cart_items")
