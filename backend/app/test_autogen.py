import asyncio
import sys
import os
sys.path.insert(0, '/app')

from services.autogen_orchestrator import AutoGenAIOrchestrator

async def test_autogen_analysis():
    print("🤖 Testing AutoGen HSE Analysis")
    print("=" * 50)
    
    # Sample permit data
    permit_data = {
        "id": 1,
        "title": "Lavoro su tetto",
        "description": "Pulizia e manutenzione pluviali",
        "work_type": "maintenance",
        "location": "Tetto edificio produzione",
        "duration_hours": 2,
        "priority_level": "medium",
        "tags": ["height_work", "cleaning"]
    }
    
    # Empty context documents (since Weaviate is disabled)
    context_documents = []
    
    # User context
    user_context = {
        "tenant_id": 1,
        "user_id": 1,
        "department": "maintenance"
    }
    
    try:
        print("🚀 Starting AutoGen analysis...")
        orchestrator = AutoGenAIOrchestrator()
        
        result = await orchestrator.run_multi_agent_analysis(
            permit_data=permit_data,
            context_documents=context_documents,
            user_context=user_context
        )
        
        print("\n✅ AutoGen Analysis Results:")
        print(f"Analysis ID: {result.get('analysis_id')}")
        print(f"Complete: {result.get('analysis_complete')}")
        print(f"Confidence: {result.get('confidence_score')}")
        print(f"Processing time: {result.get('processing_time')}s")
        print(f"Agents involved: {result.get('agents_involved')}")
        
        if result.get('error'):
            print(f"❌ Error: {result.get('error')}")
        
        # Check executive summary
        exec_summary = result.get('executive_summary', {})
        print(f"\n📊 Executive Summary:")
        print(f"Overall score: {exec_summary.get('overall_score')}")
        print(f"Critical issues: {exec_summary.get('critical_issues')}")
        print(f"Compliance level: {exec_summary.get('compliance_level')}")
        
        # Performance metrics
        metrics = result.get('performance_metrics', {})
        print(f"\n📈 Performance:")
        print(f"Analysis method: {metrics.get('analysis_method')}")
        print(f"Conversation rounds: {metrics.get('autogen_conversation_rounds')}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(test_autogen_analysis())