"""Add level field to SystemLog model

Revision ID: add_level_to_systemlog
Revises: 172d724fdfe6
Create Date: 2025-07-28 18:35:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_level_to_systemlog'
down_revision = '172d724fdfe6'
branch_labels = None
depends_on = None


def upgrade():
    # Add level column to system_logs table
    op.add_column('system_logs', sa.Column('level', sa.String(20), nullable=True, server_default='info'))


def downgrade():
    # Remove level column from system_logs table
    op.drop_column('system_logs', 'level') 