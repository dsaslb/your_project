"""Add assignee and SLA fields to attendance disputes

Revision ID: add_assignee_to_attendance_disputes
Revises: 20250127_add_attendance_dispute
Create Date: 2025-01-28 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = 'add_assignee_to_attendance_disputes'
down_revision = '20250127_add_attendance_dispute'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col['name'] for col in inspector.get_columns('attendance_disputes')]
    with op.batch_alter_table('attendance_disputes', schema=None) as batch_op:
        if 'assignee_id' not in columns:
            batch_op.add_column(sa.Column('assignee_id', sa.Integer(), nullable=True))
            batch_op.create_foreign_key('fk_attendance_disputes_assignee_id', 'users', ['assignee_id'], ['id'])
            batch_op.create_index(batch_op.f('ix_attendance_disputes_assignee_id'), ['assignee_id'], unique=False)
        if 'sla_due' not in columns:
            batch_op.add_column(sa.Column('sla_due', sa.DateTime(), nullable=True))
            batch_op.create_index(batch_op.f('ix_attendance_disputes_sla_due'), ['sla_due'], unique=False)


def downgrade():
    with op.batch_alter_table('attendance_disputes', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_attendance_disputes_sla_due'), table_name='attendance_disputes')
        batch_op.drop_index(batch_op.f('ix_attendance_disputes_assignee_id'), table_name='attendance_disputes')
        batch_op.drop_constraint('fk_attendance_disputes_assignee_id', type_='foreignkey')
        batch_op.drop_column('sla_due')
        batch_op.drop_column('assignee_id') 