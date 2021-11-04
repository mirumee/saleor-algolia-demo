"""add configuration_webhook types

Revision ID: 40bf78d835eb
Revises: 053c3e91f6be
Create Date: 2021-07-22 08:30:58.756666

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import table

# revision identifiers, used by Alembic.
revision = "40bf78d835eb"
down_revision = "053c3e91f6be"
branch_labels = None
depends_on = None

TYPES_TO_FILL = [
    "PRODUCT_CREATED",
    "PRODUCT_UPDATED",
    "PRODUCT_DELETED",
    "PRODUCT_VARIANT_CREATED",
    "PRODUCT_VARIANT_UPDATED",
    "PRODUCT_VARIANT_DELETED",
]


def upgrade():
    configuration_webhook = table(
        "configuration_webhooks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=255), nullable=True),
    )
    op.execute(
        configuration_webhook.insert().values(
            [{"type": entry} for entry in TYPES_TO_FILL]
        )
    )


def downgrade():
    configuration_webhook = table(
        "configuration_webhooks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=255), nullable=True),
    )
    op.execute(
        configuration_webhook.delete().where(
            configuration_webhook.c.type.in_(TYPES_TO_FILL)
        )
    )
