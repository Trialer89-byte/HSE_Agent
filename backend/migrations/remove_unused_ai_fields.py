"""
Remove unused ai_keywords and ai_categories columns from documents table
These fields are stored in Weaviate vector database instead
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    """Remove unused AI fields from documents table"""
    op.drop_column('documents', 'ai_keywords')
    op.drop_column('documents', 'ai_categories')

def downgrade():
    """Re-add AI fields to documents table"""
    op.add_column('documents', 
        sa.Column('ai_keywords', postgresql.JSON, nullable=True, server_default='[]')
    )
    op.add_column('documents', 
        sa.Column('ai_categories', postgresql.JSON, nullable=True, server_default='[]')
    )