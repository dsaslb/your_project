"""merge all heads

Revision ID: 0195ae3e5f1f
Revises: add_assignee_to_attendance_disputes, add_attendance_dispute_model, d7e7480178c0
Create Date: 2025-06-27 18:26:30.277422

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0195ae3e5f1f'
down_revision = ('add_assignee_to_attendance_disputes', 'add_attendance_dispute_model', 'd7e7480178c0')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
