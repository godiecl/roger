"""Add expert_detection_annotations and expert_description_annotations tables

Revision ID: 010
Revises: 009
Create Date: 2026-05-19 00:01:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = '010'
down_revision: Union[str, None] = '009'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()

    if 'expert_detection_annotations' not in existing_tables:
        op.create_table(
            'expert_detection_annotations',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('detection_id', sa.Integer(),
                      sa.ForeignKey('object_detections.id', ondelete='CASCADE'),
                      nullable=False, index=True),
            sa.Column('detected_object_id', sa.Integer(),
                      sa.ForeignKey('detected_objects.id', ondelete='CASCADE'),
                      nullable=True, index=True),
            sa.Column('annotator_id', sa.Integer(), nullable=False, index=True),
            sa.Column('verdict', sa.String(20), nullable=False),   # correct|incorrect|uncertain
            sa.Column('corrected_label', sa.String(255), nullable=True),
            sa.Column('corrected_category', sa.String(50), nullable=True),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True),
                      server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        )

    if 'expert_description_annotations' not in existing_tables:
        op.create_table(
            'expert_description_annotations',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('photograph_id', sa.Integer(),
                      sa.ForeignKey('photographs.id', ondelete='CASCADE'),
                      nullable=False, index=True),
            sa.Column('annotator_id', sa.Integer(), nullable=False, index=True),
            sa.Column('ai_rating', sa.Integer(), nullable=True),           # 1-5
            sa.Column('reference_description', sa.Text(), nullable=False),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True),
                      server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()

    if 'expert_description_annotations' in existing_tables:
        op.drop_table('expert_description_annotations')
    if 'expert_detection_annotations' in existing_tables:
        op.drop_table('expert_detection_annotations')
