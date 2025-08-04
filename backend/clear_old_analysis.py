#!/usr/bin/env python3
"""
Script to clear old AI analysis data from database
This forces new analysis to be generated with correct format
"""
import sys
sys.path.append('/app')

def clear_old_analysis():
    """Clear old analysis data to force regeneration"""
    print("To clear old analysis data from database:")
    print("1. Connect to your database")
    print("2. Run: UPDATE work_permits SET ai_analysis = NULL, analyzed_at = NULL WHERE ai_analysis IS NOT NULL;")
    print("3. This will force new analysis to be generated with correct Citation format")
    
    print("\nSQL command:")
    print("UPDATE work_permits SET ai_analysis = NULL, analyzed_at = NULL WHERE ai_analysis IS NOT NULL;")

if __name__ == "__main__":
    clear_old_analysis()