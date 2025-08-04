#!/usr/bin/env python3
"""
Test script to verify Citation validation fix by directly testing the response
"""
import asyncio
import sys
import os
sys.path.append('/app')

from app.services.mock_orchestrator import MockOrchestrator
from app.schemas.work_permit import PermitAnalysisResponse
import json
import time

async def test_citation_fix():
    """Test the MockOrchestrator citations are properly formatted"""
    
    print("Testing Citation validation fix...")
    
    # Create mock permit data for chemical work (has multiple citations)
    permit_data = {
        "id": 999,
        "title": "Test Lavoro Chimico",
        "description": "Test di verifica Citation objects",  
        "work_type": "chimico",
        "location": "Test Location"
    }
    
    context_documents = []
    user_context = {
        "tenant_id": 1,
        "user_id": 1,
        "department": "test"
    }
    
    # Create orchestrator and run analysis
    orchestrator = MockOrchestrator()
    
    try:
        result = await orchestrator.run_mock_analysis(
            permit_data=permit_data,
            context_documents=context_documents,
            user_context=user_context,
            vector_service=None
        )
        
        print("MockOrchestrator analysis completed")
        
        # Test Pydantic validation
        try:
            # This will validate the response structure
            response = PermitAnalysisResponse(**result)
            print("Pydantic validation successful!")
            
            # Check citations structure
            citations = result.get("citations", {})
            normative_citations = citations.get("normative", [])
            
            print(f"\nFound {len(normative_citations)} normative citations:")
            for i, citation in enumerate(normative_citations):
                doc_info = citation.get("document_info", {})
                print(f"  {i+1}. {doc_info.get('title')} (type: {doc_info.get('type')})")
            
            # Verify compliance_check normative_references
            compliance = result.get("compliance_check", {})
            norm_refs = compliance.get("normative_references", [])
            print(f"\nCompliance check has {len(norm_refs)} normative references")
            
            return True
            
        except Exception as validation_error:
            print(f"Pydantic validation failed: {validation_error}")
            print(f"This indicates Citation objects are still not properly formatted")
            return False
            
    except Exception as e:
        print(f"MockOrchestrator failed: {e}")
        return False

async def main():
    print("Testing Citation Validation Fix")
    print("=" * 50)
    
    success = await test_citation_fix()
    
    print("\n" + "=" * 50)
    if success:
        print("Citation validation fix verified! Response structure is correct.")
    else:
        print("Citation validation issue still exists.")

if __name__ == "__main__":
    asyncio.run(main())