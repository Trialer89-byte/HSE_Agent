#!/usr/bin/env python3
"""
Test to reproduce the exact Citation validation error from the API
"""
import sys
sys.path.append('/app')

from app.schemas.work_permit import PermitAnalysisResponse
import json

# This is the exact structure that causes the error based on the error message
problematic_response = {
    "analysis_id": "test_123",
    "permit_id": 1,
    "confidence_score": 0.75,
    "processing_time": 1.5,
    "timestamp": "2025-08-03T17:21:10.766168",
    
    "executive_summary": {
        "overall_score": 0.7,
        "critical_issues": 0,
        "recommendations": 3,
        "compliance_level": "parziale",
        "estimated_completion_time": "2-4 ore",
        "key_findings": ["Test finding"],
        "next_steps": ["Test step"]
    },
    
    "action_items": [],
    
    # This is where the error occurs - strings instead of Citation objects
    "citations": {
        "normative": ["REACH", "CLP", "D.Lgs 81/2008"],  # This causes the error!
        "procedures": [],
        "guidelines": []
    },
    
    "completion_roadmap": {
        "immediate": ["Test"],
        "short_term": ["Test"],
        "long_term": ["Test"]
    },
    
    "performance_metrics": {
        "total_processing_time": 1.5,
        "agents_successful": 1,
        "agents_total": 1,
        "analysis_method": "Test"
    },
    
    "timestamp": "2025-08-03T17:21:10.766168",
    "agents_involved": ["TestAgent"],
    "ai_version": "Test-1.0"
}

# Test with proper Citation objects
proper_response = problematic_response.copy()
proper_response["citations"] = {
    "normative": [
        {
            "document_info": {
                "title": "REACH",
                "type": "regolamento",
                "code": "REACH"
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
        },
        {
            "document_info": {
                "title": "CLP",
                "type": "regolamento",
                "code": "CLP"
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
        },
        {
            "document_info": {
                "title": "D.Lgs 81/2008",
                "type": "normativa",
                "code": "D.Lgs 81/2008"
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
    ],
    "procedures": [],
    "guidelines": []
}

def test_problematic_response():
    print("Testing problematic response (strings in normative)...")
    try:
        response = PermitAnalysisResponse(**problematic_response)
        print("ERROR: This should have failed but didn't!")
        return False
    except Exception as e:
        print(f"Expected error occurred: {e}")
        return True

def test_proper_response():
    print("\nTesting proper response (Citation objects)...")
    try:
        response = PermitAnalysisResponse(**proper_response)
        print("SUCCESS: Proper Citation objects validated correctly!")
        return True
    except Exception as e:
        print(f"ERROR: Validation failed: {e}")
        return False

if __name__ == "__main__":
    print("Citation Validation Error Reproduction Test")
    print("=" * 50)
    
    # Test 1: Reproduce the error
    error_reproduced = test_problematic_response()
    
    # Test 2: Show correct format
    proper_format_works = test_proper_response()
    
    print("\n" + "=" * 50)
    print(f"Error reproduction: {'SUCCESS' if error_reproduced else 'FAILED'}")
    print(f"Proper format test: {'SUCCESS' if proper_format_works else 'FAILED'}")
    
    if error_reproduced:
        print("\nThe error occurs when citations.normative contains strings instead of Citation objects.")
        print("This means somewhere in the code, the normative field is being set to a list of strings.")