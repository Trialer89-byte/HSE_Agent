#!/usr/bin/env python3
"""
Test script to verify datetime serialization fix by directly calling mock orchestrator
"""
import asyncio
import sys
import os
sys.path.append('/app')

from app.services.mock_orchestrator import MockOrchestrator
import json
import time

async def test_mock_orchestrator():
    """Test the MockOrchestrator directly to verify datetime serialization"""
    
    print("🧪 Testing MockOrchestrator datetime serialization...")
    
    # Create mock permit data
    permit_data = {
        "id": 999,
        "title": "Test Lavoro Meccanico",
        "description": "Test di verifica serializzazione datetime",  
        "work_type": "meccanico",
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
    
    start_time = time.time()
    try:
        result = await orchestrator.run_mock_analysis(
            permit_data=permit_data,
            context_documents=context_documents,
            user_context=user_context,
            vector_service=None
        )
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        print(f"✅ MockOrchestrator completed in {elapsed:.3f} seconds")
        
        # Test JSON serialization
        try:
            json_result = json.dumps(result)
            print(f"✅ JSON serialization successful ({len(json_result)} chars)")
            
            # Check key fields
            print(f"📊 Analysis ID: {result.get('analysis_id')}")
            print(f"⏰ Timestamp: {result.get('timestamp')}")
            print(f"🤖 AI Version: {result.get('ai_version')}")
            print(f"📈 Confidence: {result.get('confidence_score')}")
            
            return True
            
        except Exception as json_error:
            print(f"❌ JSON serialization failed: {json_error}")
            print(f"💡 This indicates datetime objects are still not properly serialized")
            
            # Find the problematic field
            for key, value in result.items():
                try:
                    json.dumps(value)
                except Exception as e:
                    print(f"❌ Field '{key}' cannot be serialized: {e}")
                    print(f"   Value type: {type(value)}")
                    print(f"   Value: {value}")
            
            return False
            
    except Exception as e:
        end_time = time.time()
        elapsed = end_time - start_time
        print(f"❌ MockOrchestrator failed after {elapsed:.3f} seconds: {e}")
        return False

async def main():
    print("🔧 Testing DateTime Serialization Fix")
    print("=" * 50)
    
    success = await test_mock_orchestrator()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ DateTime serialization fix verified! MockOrchestrator works correctly.")
        print("💡 The main blocking issue should be resolved.")
    else:
        print("❌ DateTime serialization issue still exists.")
        print("💡 Need to investigate further.")

if __name__ == "__main__":
    asyncio.run(main())