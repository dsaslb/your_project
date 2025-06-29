"""merge feedback_issues branch

Revision ID: f55f40adae8d
Revises: f91f70efbdaf, 738cbdf6049f
Create Date: 2025-06-29 08:41:41.053958

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f55f40adae8d'
down_revision = ('f91f70efbdaf', '738cbdf6049f')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
