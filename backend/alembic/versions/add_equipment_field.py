"""Add equipment field to work_permits

Revision ID: add_equipment_field
Revises: add_consolidated_actions_column
Create Date: 2025-09-15

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_equipment_field'
down_revision = 'add_consolidated_actions'
branch_labels = None
depends_on = None


def upgrade():
    # Add equipment column to work_permits table
    op.add_column('work_permits',
        sa.Column('equipment', sa.JSON(), nullable=True, default=[])
    )

    # Set default value for existing records
    op.execute("""
        UPDATE work_permits
        SET equipment = '[]'::jsonb
        WHERE equipment IS NULL
    """)


def downgrade():
    # Remove the column
    op.drop_column('work_permits', 'equipment')