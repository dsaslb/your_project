"""merge heads

Revision ID: ad1fb0b00a4c
Revises: add_brand_onboarding_tables, d2ea43c83dc9
Create Date: 2025-07-15 20:31:38.315307

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ad1fb0b00a4c"
down_revision = ("add_brand_onboarding_tables", "d2ea43c83dc9")
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
