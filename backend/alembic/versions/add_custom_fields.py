"""Add custom_fields to work_permits

Revision ID: add_custom_fields
Revises: add_equipment_field
Create Date: 2025-09-15

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_custom_fields'
down_revision = 'add_equipment_field'
branch_labels = None
depends_on = None


def upgrade():
    # Add custom_fields column to work_permits table
    op.add_column('work_permits',
        sa.Column('custom_fields', sa.JSON(), nullable=True, default={})
    )

    # Set default value for existing records
    op.execute("""
        UPDATE work_permits
        SET custom_fields = '{}'::jsonb
        WHERE custom_fields IS NULL
    """)


def downgrade():
    # Remove the column
    op.drop_column('work_permits', 'custom_fields')