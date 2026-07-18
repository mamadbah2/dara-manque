"""add card_uid to patients

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-07-18

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "patients",
        sa.Column("card_uid", sa.String(), nullable=True),
    )
    op.create_index(
        "ix_patients_card_uid", "patients", ["card_uid"], unique=True
    )


def downgrade() -> None:
    op.drop_index("ix_patients_card_uid", table_name="patients")
    op.drop_column("patients", "card_uid")
