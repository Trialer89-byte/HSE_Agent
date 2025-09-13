"""Add risk_level, start_date, end_date fields to work_permits

Revision ID: add_risk_level_dates
Revises: add_risk_mitigation
Create Date: 2025-08-31

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_risk_level_dates'
down_revision = 'add_risk_mitigation'
branch_labels = None
depends_on = None


def upgrade():
    # Add risk_level column
    op.add_column('work_permits', 
        sa.Column('risk_level', sa.String(20), nullable=True, default='medium')
    )
    
    # Add start_date column
    op.add_column('work_permits', 
        sa.Column('start_date', sa.DateTime(), nullable=True)
    )
    
    # Add end_date column
    op.add_column('work_permits', 
        sa.Column('end_date', sa.DateTime(), nullable=True)
    )
    
    # Set default value for existing records
    op.execute("""
        UPDATE work_permits 
        SET risk_level = 'medium' 
        WHERE risk_level IS NULL
    """)


def downgrade():
    # Remove the columns
    op.drop_column('work_permits', 'end_date')
    op.drop_column('work_permits', 'start_date')
    op.drop_column('work_permits', 'risk_level')