"""
Script to apply the migration that removes unused ai_keywords and ai_categories columns
"""

import sys
import os
from sqlalchemy import create_engine, text
from app.config.settings import settings

def apply_migration():
    """Apply the migration to remove unused AI fields"""
    
    # Create database connection
    engine = create_engine(settings.database_url)
    
    try:
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                # Check if columns exist
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'documents' 
                    AND column_name IN ('ai_keywords', 'ai_categories')
                """))
                
                columns_to_remove = [row[0] for row in result]
                
                if not columns_to_remove:
                    print("✓ Columns ai_keywords and ai_categories have already been removed")
                    return True
                
                print(f"Found columns to remove: {columns_to_remove}")
                
                # Drop the columns
                for column in columns_to_remove:
                    print(f"Dropping column: {column}")
                    conn.execute(text(f"ALTER TABLE documents DROP COLUMN IF EXISTS {column}"))
                
                # Commit the transaction
                trans.commit()
                print("✓ Migration completed successfully")
                
                # Verify the columns are removed
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'documents' 
                    AND column_name IN ('ai_keywords', 'ai_categories')
                """))
                
                remaining = [row[0] for row in result]
                if remaining:
                    print(f"⚠ Warning: These columns still exist: {remaining}")
                    return False
                else:
                    print("✓ Verified: Columns successfully removed")
                    return True
                    
            except Exception as e:
                trans.rollback()
                print(f"✗ Error during migration: {e}")
                return False
                
    except Exception as e:
        print(f"✗ Could not connect to database: {e}")
        return False
    finally:
        engine.dispose()

if __name__ == "__main__":
    success = apply_migration()
    sys.exit(0 if success else 1)