"""
Add keywords column to documents table
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'add_keywords_to_documents'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Add keywords column to documents table"""
    op.add_column('documents', 
        sa.Column('keywords', postgresql.JSON, nullable=True, server_default='[]')
    )
    
    # Update existing documents to have empty keywords array
    op.execute("UPDATE documents SET keywords = '[]'::jsonb WHERE keywords IS NULL")


def downgrade():
    """Remove keywords column from documents table"""
    op.drop_column('documents', 'keywords')