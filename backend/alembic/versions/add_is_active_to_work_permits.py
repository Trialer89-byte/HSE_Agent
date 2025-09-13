"""Add is_active field to work_permits

Revision ID: add_is_active_work_permits
Revises: add_risk_mitigation
Create Date: 2025-08-30

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_is_active_work_permits'
down_revision = 'add_risk_mitigation'
branch_labels = None
depends_on = None


def upgrade():
    # Add is_active column to work_permits table
    op.add_column('work_permits', 
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True)
    )
    
    # Set default value for existing records
    op.execute("""
        UPDATE work_permits 
        SET is_active = TRUE 
        WHERE is_active IS NULL
    """)
    
    # Make the column not nullable after setting defaults
    op.alter_column('work_permits', 'is_active', nullable=False)


def downgrade():
    # Remove the column
    op.drop_column('work_permits', 'is_active')