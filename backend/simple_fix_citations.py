#!/usr/bin/env python3
"""
Simple script to demonstrate the fix for Citation validation
This shows what needs to be fixed without requiring database dependencies
"""

# Example of problematic data structure (what causes the error)
problematic_analysis = {
    "analysis_id": "test_123",
    "permit_id": 1,
    "confidence_score": 0.75,
    "processing_time": 1.5,
    "citations": {
        "normative": ["REACH", "CLP", "D.Lgs 81/2008"],  # These strings cause the error
        "procedures": [],
        "guidelines": []
    },
    # ... other required fields
}

# Function to convert strings to proper Citation objects
def convert_string_to_citation(ref_string: str) -> dict:
    """Convert a string reference to a proper Citation object"""
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

def fix_citations_structure(data: dict) -> dict:
    """Fix citations in data structure if they are strings"""
    if "citations" in data:
        citations = data["citations"]
        
        # Fix each citation category
        for category in ["normative", "procedures", "guidelines"]:
            if category in citations and isinstance(citations[category], list):
                fixed_items = []
                for item in citations[category]:
                    if isinstance(item, str):
                        # Convert string to Citation object
                        fixed_items.append(convert_string_to_citation(item))
                    else:
                        # Already a proper Citation object
                        fixed_items.append(item)
                citations[category] = fixed_items
    
    return data

def main():
    print("Citation Fix Demonstration")
    print("=" * 50)
    
    print("Problematic structure (causes validation error):")
    print(f"  normative: {problematic_analysis['citations']['normative']}")
    
    # Apply fix
    fixed_analysis = fix_citations_structure(problematic_analysis.copy())
    
    print("\nFixed structure (proper Citation objects):")
    for i, citation in enumerate(fixed_analysis['citations']['normative']):
        doc_info = citation['document_info']
        print(f"  {i+1}. {doc_info['title']} (type: {doc_info['type']})")
    
    print("\nTo fix existing database records:")
    print("1. Connect to the database")
    print("2. Query all WorkPermit records with ai_analysis data")
    print("3. Apply fix_citations_structure() to each record's ai_analysis")
    print("4. Save the updated records back to the database")
    
    print("\nThis fix converts:")
    print("  FROM: \"citations\": {\"normative\": [\"REACH\", \"CLP\", \"D.Lgs 81/2008\"]}")
    print("  TO:   \"citations\": {\"normative\": [{\"document_info\": {...}, ...}, ...]}")

if __name__ == "__main__":
    main()