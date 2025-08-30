"""Add risk_mitigation_actions field to work_permits

Revision ID: add_risk_mitigation
Revises: 
Create Date: 2025-08-20

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_risk_mitigation'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add risk_mitigation_actions column to work_permits table
    op.add_column('work_permits', 
        sa.Column('risk_mitigation_actions', sa.JSON(), nullable=True, default=[])
    )
    
    # Set default value for existing records
    op.execute("""
        UPDATE work_permits 
        SET risk_mitigation_actions = '[]'::jsonb 
        WHERE risk_mitigation_actions IS NULL
    """)


def downgrade():
    # Remove the column
    op.drop_column('work_permits', 'risk_mitigation_actions')