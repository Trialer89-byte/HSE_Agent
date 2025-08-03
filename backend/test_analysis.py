import asyncio
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config.settings import settings
from app.services.ai_orchestrator import AIOrchestrator

async def test_analysis():
    print("Testing AI Orchestrator...")
    
    # Simple permit data
    permit_data = {
        "id": 1,
        "title": "lavoro su tetto",
        "description": "pulire pluviali",
        "work_type": "chimico",
        "location": "produzione"
    }
    
    # Empty context documents (since we disabled Weaviate)
    context_documents = []
    
    # User context
    user_context = {
        "tenant_id": 1,
        "user_id": 1,
        "department": "maintenance"
    }
    
    try:
        orchestrator = AIOrchestrator()
        print("Starting analysis...")
        
        result = await orchestrator.run_multi_agent_analysis(
            permit_data=permit_data,
            context_documents=context_documents,
            user_context=user_context
        )
        
        print(f"\nAnalysis completed!")
        print(f"Confidence: {result.get('confidence_score')}")
        print(f"Processing time: {result.get('processing_time')}s")
        print(f"Agents involved: {result.get('agents_involved')}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

# Run the test
asyncio.run(test_analysis())