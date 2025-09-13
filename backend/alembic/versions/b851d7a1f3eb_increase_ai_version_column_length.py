"""Increase ai_version column length to 50 characters

Revision ID: b851d7a1f3eb
Revises: add_is_active_to_work_permits
Create Date: 2025-08-31

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b851d7a1f3eb'
down_revision = 'add_is_active_work_permits'
branch_labels = None
depends_on = None


def upgrade():
    # Increase ai_version column length from 20 to 50 characters
    op.alter_column('work_permits', 'ai_version',
                    existing_type=sa.VARCHAR(length=20),
                    type_=sa.VARCHAR(length=50),
                    existing_nullable=True)


def downgrade():
    # Revert ai_version column length back to 20 characters
    op.alter_column('work_permits', 'ai_version',
                    existing_type=sa.VARCHAR(length=50),
                    type_=sa.VARCHAR(length=20),
                    existing_nullable=True)