"""
Add file_hash column to documents table

Run this migration to add the file_hash column for duplicate detection:
python migrations/add_file_hash_to_documents.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.config.database import engine


def upgrade():
    """Add file_hash column to documents table"""
    with engine.connect() as conn:
        # Check if column already exists
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='documents' AND column_name='file_hash'
        """))
        
        if not result.fetchone():
            # Add the column
            conn.execute(text("""
                ALTER TABLE documents 
                ADD COLUMN file_hash VARCHAR(64)
            """))
            
            # Create index on file_hash for faster lookups
            conn.execute(text("""
                CREATE INDEX idx_documents_file_hash 
                ON documents(file_hash)
            """))
            
            conn.commit()
            print("Successfully added file_hash column to documents table")
        else:
            print("file_hash column already exists")


def downgrade():
    """Remove file_hash column from documents table"""
    with engine.connect() as conn:
        conn.execute(text("""
            ALTER TABLE documents 
            DROP COLUMN IF EXISTS file_hash
        """))
        conn.commit()
        print("Successfully removed file_hash column from documents table")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database migration for file_hash column")
    parser.add_argument("--downgrade", action="store_true", help="Revert the migration")
    args = parser.parse_args()
    
    if args.downgrade:
        downgrade()
    else:
        upgrade()