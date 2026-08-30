"""add_screening_result_to_eye_analysis

Revision ID: c1d5e3f4a5b6
Revises: b8e4f1a2930c
Create Date: 2026-08-31 03:09:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1d5e3f4a5b6'
down_revision: Union[str, None] = 'b8e4f1a2930c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'eye_analysis_sessions',
        sa.Column('screening_result', sa.JSON(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('eye_analysis_sessions', 'screening_result')

