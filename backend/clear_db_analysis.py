#!/usr/bin/env python3
"""
Python script to clear old AI analysis data from database
Run this inside Docker container or with proper database connection
"""
import sys
sys.path.append('/app')

try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    from app.config.settings import settings
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

def clear_analysis_data():
    """Clear old analysis data from database"""
    if not SQLALCHEMY_AVAILABLE:
        print("SQLAlchemy not available. Use the SQL script instead:")
        print("Execute: clear_old_analysis.sql")
        return False
    
    try:
        # Use database URL from settings
        database_url = settings.database_url
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Check current status
            result = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_permits,
                    COUNT(ai_analysis) as permits_with_analysis
                FROM work_permits
            """))
            
            row = result.fetchone()
            total_permits = row[0]
            permits_with_analysis = row[1]
            
            print(f"Database status:")
            print(f"  Total permits: {total_permits}")
            print(f"  Permits with AI analysis: {permits_with_analysis}")
            
            if permits_with_analysis == 0:
                print("No analysis data to clear.")
                return True
            
            # Create backup table
            print("\n1. Creating backup table...")
            conn.execute(text("""
                DROP TABLE IF EXISTS work_permits_analysis_backup
            """))
            
            conn.execute(text("""
                CREATE TABLE work_permits_analysis_backup AS
                SELECT 
                    id, title, ai_analysis, ai_confidence, ai_version, analyzed_at,
                    content_analysis, risk_assessment, compliance_check, 
                    dpi_recommendations, action_items
                FROM work_permits 
                WHERE ai_analysis IS NOT NULL
            """))
            
            # Clear analysis data
            print("2. Clearing analysis data...")
            result = conn.execute(text("""
                UPDATE work_permits 
                SET 
                    ai_analysis = NULL,
                    ai_confidence = 0.0,
                    ai_version = NULL,
                    analyzed_at = NULL,
                    content_analysis = NULL,
                    risk_assessment = NULL,
                    compliance_check = NULL,
                    dpi_recommendations = NULL,
                    action_items = NULL
                WHERE ai_analysis IS NOT NULL
            """))
            
            updated_rows = result.rowcount
            print(f"   Updated {updated_rows} records")
            
            # Verify cleanup
            result = conn.execute(text("""
                SELECT COUNT(ai_analysis) FROM work_permits WHERE ai_analysis IS NOT NULL
            """))
            remaining = result.fetchone()[0]
            
            # Commit transaction
            conn.commit()
            
            print(f"3. Verification:")
            print(f"   Records with analysis remaining: {remaining}")
            print(f"   Backup created with {permits_with_analysis} records")
            
            if remaining == 0:
                print("\n✅ Successfully cleared all old analysis data!")
                return True
            else:
                print(f"\n⚠️  Warning: {remaining} records still have analysis data")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("Clear Old AI Analysis Data")
    print("=" * 50)
    
    success = clear_analysis_data()
    
    if success:
        print("\n🎉 Database cleanup completed!")
        print("Next steps:")
        print("1. Test the API - it should generate fresh analysis")
        print("2. Re-enable cache in permits.py after testing")
    else:
        print("\n❌ Cleanup failed. Check the error messages above.")

if __name__ == "__main__":
    main()