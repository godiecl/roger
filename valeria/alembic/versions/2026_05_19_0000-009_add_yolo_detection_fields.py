"""Add bbox and mask_polygon fields to detected_objects for YOLOv8 output

Revision ID: 009
Revises: 008
Create Date: 2026-05-19 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = '009'
down_revision: Union[str, None] = '008'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # object_detections puede no existir si la app aún no la creó
    if 'object_detections' not in inspector.get_table_names():
        return

    if 'detected_objects' not in inspector.get_table_names():
        return

    existing = {c['name'] for c in inspector.get_columns('detected_objects')}

    for col_name, col_def in [
        ('bbox_x1',       sa.Column('bbox_x1',       sa.Float(), nullable=True)),
        ('bbox_y1',       sa.Column('bbox_y1',       sa.Float(), nullable=True)),
        ('bbox_x2',       sa.Column('bbox_x2',       sa.Float(), nullable=True)),
        ('bbox_y2',       sa.Column('bbox_y2',       sa.Float(), nullable=True)),
        ('mask_polygon',  sa.Column('mask_polygon',  sa.Text(),  nullable=True)),
    ]:
        if col_name not in existing:
            op.add_column('detected_objects', col_def)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if 'detected_objects' not in inspector.get_table_names():
        return

    existing = {c['name'] for c in inspector.get_columns('detected_objects')}
    for col_name in ('bbox_x1', 'bbox_y1', 'bbox_x2', 'bbox_y2', 'mask_polygon'):
        if col_name in existing:
            op.drop_column('detected_objects', col_name)
