"""
Test enhanced AutoGen agents with hot work detection
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import asyncio
import json
from app.agents.enhanced_autogen_agents import EnhancedAutoGenHSEAgents
from app.agents.simple_autogen_agents import SimpleAutoGenHSEAgents

async def test_hot_work_detection():
    """Test if agents detect hot work from misspelled 'welsing'"""
    
    # Test permit with misspelled welding
    permit_data = {
        "id": 6,
        "title": "Repair oil pipe with welsing and cutting",
        "description": "Need to repair damaged oil pipeline using welsing equipment and cutting tools",
        "work_type": "maintenance",
        "location": "Tank farm area",
        "duration_hours": 4,
        "workers_count": 2,
        "equipment": "Welsing machine, cutting equipment, grinder"
    }
    
    # Test documents (simulated)
    context_documents = [
        {
            "title": "Procedura Lavori a Caldo HSE-PRO-001",
            "content": "Tutti i lavori di saldatura, taglio termico e molatura richiedono hot work permit...",
            "document_type": "procedura_sicurezza"
        }
    ]
    
    user_context = {"tenant_id": 1}
    
    print("\n" + "="*80)
    print("TESTING ENHANCED AGENTS")
    print("="*80)
    
    try:
        # Test enhanced agents
        enhanced_agents = EnhancedAutoGenHSEAgents(user_context)
        print(f"\nEnhanced agents initialized: {len(enhanced_agents.agents)} specialists")
        print(f"Available specialists: {list(enhanced_agents.agents.keys())}")
        
        # Run analysis
        result = await enhanced_agents.analyze_permit(permit_data, context_documents)
        
        if result.get("analysis_complete"):
            print("\n✅ Enhanced analysis completed successfully!")
            print(f"Agents involved: {result.get('agents_involved', [])}")
            print(f"Confidence score: {result.get('confidence_score', 0)}")
            
            # Check if hot work was detected
            final_analysis = result.get("final_analysis", {})
            executive_summary = final_analysis.get("executive_summary", {})
            
            print(f"\nKey findings:")
            for finding in executive_summary.get("key_findings", []):
                print(f"  - {finding}")
            
            # Check action items for hot work related items
            hot_work_detected = False
            for item in final_analysis.get("action_items", []):
                if any(keyword in item.get("description", "").lower() 
                       for keyword in ["saldatura", "welding", "hot work", "lavori a caldo", "fiamma"]):
                    hot_work_detected = True
                    print(f"\n🔥 Hot work controls detected: {item.get('title')}")
            
            if hot_work_detected:
                print("\n✅ SUCCESS: Hot work risks properly identified from 'welsing' typo!")
            else:
                print("\n⚠️ WARNING: Hot work risks may not have been fully identified")
                
        else:
            print(f"\n❌ Analysis failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n❌ Error testing enhanced agents: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("COMPARING WITH SIMPLE AGENTS")
    print("="*80)
    
    try:
        # Test simple agents for comparison
        simple_agents = SimpleAutoGenHSEAgents(user_context)
        print(f"\nSimple agents initialized: {len(simple_agents.agents)} agents")
        print(f"Available agents: {list(simple_agents.agents.keys())}")
        
        result = await simple_agents.analyze_permit(permit_data, context_documents)
        
        if result.get("analysis_complete"):
            print("\n✅ Simple analysis completed")
            print(f"Agents involved: {result.get('agents_involved', [])}")
            
            # Note the difference in agent count
            print("\n📊 COMPARISON:")
            print(f"  Enhanced agents: 8 specialists (including hot work expert)")
            print(f"  Simple agents: {len(simple_agents.agents)} basic agents")
            
    except Exception as e:
        print(f"\n❌ Error testing simple agents: {e}")

if __name__ == "__main__":
    print("\nTesting AutoGen HSE Agents Hot Work Detection...")
    print("Testing with permit containing 'welsing' (misspelled welding)")
    
    asyncio.run(test_hot_work_detection())