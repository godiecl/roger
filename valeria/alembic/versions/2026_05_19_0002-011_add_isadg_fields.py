"""Add ISAD(G) fields to photographs table

Revision ID: 011
Revises: 010
Create Date: 2026-05-19 00:02:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = '011'
down_revision: Union[str, None] = '010'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLE = 'photographs'
_NEW_COLUMNS = [
    ('reference_code',          sa.String(100)),
    ('level_of_description',    sa.String(20)),
    ('extent',                  sa.String(255)),
    ('archival_history',        sa.Text()),
    ('scope_content',           sa.Text()),
    ('access_conditions',       sa.String(255)),
    ('reproduction_conditions', sa.String(255)),
    ('language_material',       sa.String(50)),
]


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_cols = {c['name'] for c in inspector.get_columns(_TABLE)}

    for col_name, col_type in _NEW_COLUMNS:
        if col_name not in existing_cols:
            op.add_column(_TABLE, sa.Column(col_name, col_type, nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_cols = {c['name'] for c in inspector.get_columns(_TABLE)}

    for col_name, _ in reversed(_NEW_COLUMNS):
        if col_name in existing_cols:
            op.drop_column(_TABLE, col_name)
