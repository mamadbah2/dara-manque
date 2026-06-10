"""add allergy_override to prescriptions

Revision ID: a1b2c3d4e5f6
Revises: 1f8d319d5fec
Create Date: 2026-06-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "1f8d319d5fec"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "prescriptions",
        sa.Column("allergy_override", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("prescriptions", "allergy_override")
