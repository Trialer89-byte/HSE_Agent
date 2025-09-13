"""Remove duration_hours column from work_permits (now calculated property)

Revision ID: remove_duration_hours
Revises: add_risk_level_dates
Create Date: 2025-08-31

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'remove_duration_hours'
down_revision = 'add_risk_level_dates'
branch_labels = None
depends_on = None


def upgrade():
    # Remove duration_hours column (now calculated from start_date - end_date)
    op.drop_column('work_permits', 'duration_hours')


def downgrade():
    # Re-add duration_hours column if rollback is needed
    op.add_column('work_permits', 
        sa.Column('duration_hours', sa.Integer(), nullable=True)
    )