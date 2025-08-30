"""
Apply keywords migration to add keywords column to documents table
"""
import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection parameters
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "hse_agent_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

def apply_migration():
    """Apply the keywords column migration"""
    conn = None
    cursor = None
    
    try:
        # Connect to database
        print(f"Connecting to database {DB_NAME}...")
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        
        # Check if keywords column already exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='documents' AND column_name='keywords'
        """)
        
        if cursor.fetchone():
            print("Keywords column already exists in documents table")
            return
        
        # Add keywords column
        print("Adding keywords column to documents table...")
        cursor.execute("""
            ALTER TABLE documents 
            ADD COLUMN keywords JSONB DEFAULT '[]'::jsonb
        """)
        
        # Update existing documents to have empty keywords array
        print("Setting default keywords for existing documents...")
        cursor.execute("""
            UPDATE documents 
            SET keywords = '[]'::jsonb 
            WHERE keywords IS NULL
        """)
        
        # Commit changes
        conn.commit()
        print("Migration applied successfully!")
        
        # Verify the column was added
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name='documents' AND column_name='keywords'
        """)
        result = cursor.fetchone()
        if result:
            print(f"Verified: Column '{result[0]}' with type '{result[1]}' added successfully")
        
    except Exception as e:
        print(f"Error applying migration: {e}")
        if conn:
            conn.rollback()
        raise
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    apply_migration()