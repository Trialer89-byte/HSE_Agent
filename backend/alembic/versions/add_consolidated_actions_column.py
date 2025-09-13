"""Add consolidated_actions field to work_permits

Revision ID: add_consolidated_actions
Revises: 
Create Date: 2025-09-11

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_consolidated_actions'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add consolidated_actions column to work_permits table
    op.add_column('work_permits', 
        sa.Column('consolidated_actions', sa.JSON(), nullable=True, default=[])
    )
    
    # Set default value for existing records
    op.execute("""
        UPDATE work_permits 
        SET consolidated_actions = '[]'::jsonb 
        WHERE consolidated_actions IS NULL
    """)


def downgrade():
    # Remove the column
    op.drop_column('work_permits', 'consolidated_actions')