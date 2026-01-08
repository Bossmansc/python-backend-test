"""Add admin field to users table

Revision ID: 002
Revises: 001
Create Date: 2024-01-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add is_admin column to users table
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), server_default='false', nullable=True))
    
    # Update existing users (first user becomes admin)
    op.execute("UPDATE users SET is_admin = true WHERE id = 1")
    
    # Make column not nullable
    op.alter_column('users', 'is_admin', nullable=False, server_default='false')


def downgrade() -> None:
    op.drop_column('users', 'is_admin')
