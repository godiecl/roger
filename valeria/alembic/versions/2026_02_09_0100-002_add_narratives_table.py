"""Add narratives table

Revision ID: 002
Revises: 001
Create Date: 2026-02-09 01:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create narratives table
    op.create_table(
        'narratives',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('image_id', sa.Integer(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('trazabilidad', sa.JSON(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('prompt', sa.Text(), nullable=True),
        sa.Column('language', sa.String(length=10), nullable=False, server_default='es'),
        sa.Column('model_used', sa.String(length=100), nullable=True),
        sa.Column('generation_time_ms', sa.Integer(), nullable=True),
        sa.Column('is_approved', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['image_id'], ['images.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_narratives_image_id', 'narratives', ['image_id'], unique=False)
    op.create_index('ix_narratives_language', 'narratives', ['language'], unique=False)
    op.create_index('ix_narratives_is_approved', 'narratives', ['is_approved'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_narratives_is_approved', table_name='narratives')
    op.drop_index('ix_narratives_language', table_name='narratives')
    op.drop_index('ix_narratives_image_id', table_name='narratives')
    op.drop_table('narratives')
