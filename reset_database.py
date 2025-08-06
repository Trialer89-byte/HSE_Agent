#!/usr/bin/env python3
"""
Script to completely reset the database
"""
import sys
import os
sys.path.append('/app')

from sqlalchemy import text
from app.config.database import SessionLocal, engine
from app.models.base import Base

def reset_database():
    print("🔄 Resetting database...")
    
    db = SessionLocal()
    try:
        # Drop all tables in reverse order to avoid foreign key constraints
        print("📋 Dropping existing tables...")
        
        # First, get all table names
        result = db.execute(text("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public'
        """))
        tables = [row[0] for row in result.fetchall()]
        
        # Drop all tables
        for table in tables:
            try:
                db.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
                print(f"   ✓ Dropped table: {table}")
            except Exception as e:
                print(f"   ✗ Error dropping {table}: {e}")
        
        db.commit()
        print("✅ All tables dropped successfully")
        
    except Exception as e:
        print(f"❌ Error during reset: {e}")
        db.rollback()
    finally:
        db.close()
    
    # Now recreate all tables with the correct structure
    print("\n📋 Creating new tables with correct structure...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!")
        
        # List created tables
        db = SessionLocal()
        result = db.execute(text("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY tablename
        """))
        tables = result.fetchall()
        
        print("\n📊 Created tables:")
        for table in tables:
            print(f"   • {table[0]}")
            
        db.close()
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")

if __name__ == "__main__":
    response = input("⚠️  WARNING: This will DELETE ALL DATA. Continue? (yes/no): ")
    if response.lower() == 'yes':
        reset_database()
    else:
        print("❌ Reset cancelled")