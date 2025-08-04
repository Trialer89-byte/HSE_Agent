#!/usr/bin/env python3
"""
Script to fix Citation validation issues in existing database records
Converts string citations to proper Citation objects
"""
import sys
import os
sys.path.append('/app')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.work_permit import WorkPermit
from app.config.settings import settings
import json

def convert_string_to_citation(ref_string: str) -> dict:
    """
    Convert a string reference to a proper Citation object
    """
    return {
        "document_info": {
            "title": ref_string,
            "type": "normativa" if "D.Lgs" in ref_string or "CEI" in ref_string else "regolamento",
            "code": ref_string.split(" - ")[0] if " - " in ref_string else ref_string
        },
        "relevance": {
            "score": 0.9,
            "context": "Riferimento normativo applicabile"
        },
        "key_requirements": [],
        "frontend_display": {
            "icon": "book",
            "color": "blue"
        }
    }

def fix_citations_in_analysis(analysis_data: dict) -> dict:
    """
    Fix citations in analysis data if they are strings
    """
    if not analysis_data:
        return analysis_data
    
    # Check if citations exist and need fixing
    if "citations" in analysis_data:
        citations = analysis_data["citations"]
        
        # Fix normative citations if they are strings
        if isinstance(citations.get("normative"), list):
            fixed_normative = []
            for item in citations["normative"]:
                if isinstance(item, str):
                    # Convert string to Citation object
                    fixed_normative.append(convert_string_to_citation(item))
                else:
                    # Already a proper Citation object
                    fixed_normative.append(item)
            citations["normative"] = fixed_normative
        
        # Fix procedures citations if they are strings
        if isinstance(citations.get("procedures"), list):
            fixed_procedures = []
            for item in citations["procedures"]:
                if isinstance(item, str):
                    fixed_procedures.append(convert_string_to_citation(item))
                else:
                    fixed_procedures.append(item)
            citations["procedures"] = fixed_procedures
        
        # Fix guidelines citations if they are strings
        if isinstance(citations.get("guidelines"), list):
            fixed_guidelines = []
            for item in citations["guidelines"]:
                if isinstance(item, str):
                    fixed_guidelines.append(convert_string_to_citation(item))
                else:
                    fixed_guidelines.append(item)
            citations["guidelines"] = fixed_guidelines
    
    return analysis_data

def main():
    """
    Main function to fix all citations in the database
    """
    print("Starting Citation Fix in Database")
    print("=" * 50)
    
    # Create database connection
    try:
        # Get database URL from settings
        database_url = settings.DATABASE_URL
        if not database_url:
            database_url = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
        
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        print(f"Connected to database successfully")
        
        # Query all work permits with AI analysis
        permits_with_analysis = db.query(WorkPermit).filter(
            WorkPermit.ai_analysis != None,
            WorkPermit.ai_analysis != {}
        ).all()
        
        print(f"Found {len(permits_with_analysis)} permits with AI analysis")
        
        fixed_count = 0
        error_count = 0
        
        for permit in permits_with_analysis:
            try:
                # Check if the analysis has citations
                if permit.ai_analysis and "citations" in permit.ai_analysis:
                    original_analysis = permit.ai_analysis.copy()
                    fixed_analysis = fix_citations_in_analysis(permit.ai_analysis)
                    
                    # Check if anything was fixed
                    if original_analysis != fixed_analysis:
                        permit.ai_analysis = fixed_analysis
                        fixed_count += 1
                        print(f"Fixed citations for permit {permit.id}: {permit.title}")
                
            except Exception as e:
                error_count += 1
                print(f"Error fixing permit {permit.id}: {e}")
        
        # Commit all changes
        if fixed_count > 0:
            db.commit()
            print(f"\nSuccessfully fixed {fixed_count} permits")
        else:
            print("\nNo permits needed fixing")
        
        if error_count > 0:
            print(f"Encountered errors in {error_count} permits")
        
        db.close()
        
    except Exception as e:
        print(f"Database connection error: {e}")
        print("Make sure the database is running and credentials are correct")

if __name__ == "__main__":
    main()