"""Add justification column to clusters table

Revision ID: 008
Revises: 007
Create Date: 2026-05-18 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = '008'
down_revision: Union[str, None] = '007'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('clusters', sa.Column('justification', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('clusters', 'justification')
