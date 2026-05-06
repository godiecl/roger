"""Add project_invitations table

Revision ID: 005
Revises: 004
Create Date: 2026-03-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'project_invitations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('invited_user_id', sa.Integer(), nullable=False),
        sa.Column('invited_by_user_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=10), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(), nullable=False,
                  server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False,
                  server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['invited_user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['invited_by_user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('project_id', 'invited_user_id', name='uq_project_invitation'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_project_invitations_invited_user_id', 'project_invitations', ['invited_user_id'])
    op.create_index('ix_project_invitations_project_id', 'project_invitations', ['project_id'])


def downgrade() -> None:
    op.drop_index('ix_project_invitations_project_id', table_name='project_invitations')
    op.drop_index('ix_project_invitations_invited_user_id', table_name='project_invitations')
    op.drop_table('project_invitations')
