"""Initial tables for users, images and collections

Revision ID: 001
Revises: 
Create Date: 2026-02-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.create_index('ix_users_role', 'users', ['role'], unique=False)
    op.create_index('ix_users_is_active', 'users', ['is_active'], unique=False)

    # Create collections table
    op.create_table(
        'collections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_collections_name', 'collections', ['name'], unique=True)

    # Create images table
    op.create_table(
        'images',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('author', sa.String(length=255), nullable=False, server_default='Robert Gerstmann'),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('collection_id', sa.Integer(), nullable=True),
        sa.Column('image_metadata', sa.JSON(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['collection_id'], ['collections.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_images_title', 'images', ['title'], unique=False)
    op.create_index('ix_images_year', 'images', ['year'], unique=False)
    op.create_index('ix_images_location', 'images', ['location'], unique=False)
    op.create_index('ix_images_is_public', 'images', ['is_public'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_images_is_public', table_name='images')
    op.drop_index('ix_images_location', table_name='images')
    op.drop_index('ix_images_year', table_name='images')
    op.drop_index('ix_images_title', table_name='images')
    op.drop_table('images')
    
    op.drop_index('ix_collections_name', table_name='collections')
    op.drop_table('collections')
    
    op.drop_index('ix_users_is_active', table_name='users')
    op.drop_index('ix_users_role', table_name='users')
    op.drop_index('ix_users_username', table_name='users')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
