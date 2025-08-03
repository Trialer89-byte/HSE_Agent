#!/usr/bin/env python3
"""
Test script for Gemini API integration with HSE system
"""

import asyncio
import sys
import os
import json
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    import google.generativeai as genai
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    async def test_gemini_basic():
        """Test basic Gemini functionality"""
        
        print("🧪 Testing Gemini API Integration")
        print("=" * 50)
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ GEMINI_API_KEY not found in .env file")
            print("   Please add: GEMINI_API_KEY=your-gemini-api-key-here")
            return False
        
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-pro')
            
            print("✅ Gemini client configured successfully")
            
            # Test basic HSE analysis
            test_prompt = """
Sei un esperto HSE che analizza permessi di lavoro industriali.

Analizza questo permesso di lavoro e rispondi SOLO in formato JSON valido:

PERMESSO DI LAVORO:
- Titolo: Manutenzione pompa centrifuga P-101
- Descrizione: Sostituzione guarnizioni e verifica tenute
- Tipo lavoro: manutenzione
- Ubicazione: Area produzione settore A
- DPI richiesti: casco, guanti, scarpe antinfortunistiche
- Durata: 4 ore

RISPONDI in questo formato JSON (senza testo aggiuntivo):
{
    "analisi_completata": true,
    "qualita_contenuto": 0.8,
    "problemi_identificati": ["lista dei problemi trovati"],
    "raccomandazioni_dpi": ["DPI aggiuntivi raccomandati"],
    "rischi_principali": ["rischi identificati"],
    "conformita_normativa": "conforme/non_conforme/parziale",
    "confidence_score": 0.85,
    "agent_name": "TestAgent"
}
"""
            
            print("🔄 Testing Gemini response...")
            
            generation_config = genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=4000,
            )
            
            response = model.generate_content(test_prompt, generation_config=generation_config)
            
            print("✅ Gemini response received")
            print("\n📋 Raw Response:")
            print("-" * 30)
            print(response.text)
            print("-" * 30)
            
            # Test JSON parsing
            try:
                parsed_json = json.loads(response.text)
                print("\n✅ JSON parsing successful!")
                print("📊 Parsed data:")
                for key, value in parsed_json.items():
                    print(f"  - {key}: {value}")
                
                # Validate required fields
                required_fields = ["analisi_completata", "confidence_score", "agent_name"]
                missing_fields = [field for field in required_fields if field not in parsed_json]
                
                if missing_fields:
                    print(f"\n⚠️  Missing required fields: {missing_fields}")
                else:
                    print("\n✅ All required fields present")
                
                return True
                
            except json.JSONDecodeError as e:
                print(f"\n❌ JSON parsing failed: {e}")
                print("   Gemini response might need prompt tuning")
                return False
                
        except Exception as e:
            print(f"❌ Gemini API error: {e}")
            return False
    
    
    async def test_hse_agent_integration():
        """Test integration with HSE agent system"""
        
        print("\n🔧 Testing HSE Agent Integration")
        print("=" * 50)
        
        try:
            from app.agents.content_analysis_agent import ContentAnalysisAgent
            
            user_context = {
                "tenant_id": 1,
                "user_id": 123,
                "department": "Engineering"
            }
            
            agent = ContentAnalysisAgent(user_context)
            
            print(f"✅ Agent created with provider: {agent.ai_provider}")
            
            # Test sample permit data
            sample_permit = {
                "id": 1,
                "title": "Test Manutenzione Pompa",
                "description": "Sostituzione guarnizioni pompa P-101",
                "work_type": "manutenzione",
                "location": "Area produzione",
                "duration_hours": 4,
                "dpi_required": ["casco", "scarpe antinfortunistiche"]
            }
            
            sample_documents = [
                {
                    "document_code": "D.Lgs 81/2008",
                    "title": "Testo Unico Sicurezza",
                    "content": "Normative sulla sicurezza sul lavoro...",
                    "document_type": "normativa",
                    "authority": "Stato Italiano"
                }
            ]
            
            print("🔄 Running agent analysis...")
            
            result = await agent.analyze(sample_permit, sample_documents)
            
            if result.get("analysis_complete"):
                print("✅ Agent analysis completed successfully!")
                print(f"   Confidence: {result.get('confidence_score', 'N/A')}")
                print(f"   Agent: {result.get('agent_name', 'N/A')}")
                return True
            else:
                print("❌ Agent analysis failed")
                print(f"   Error: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Agent integration test failed: {e}")
            return False
    
    
    async def main():
        """Main test function"""
        
        print("🚀 HSE Enterprise System - Gemini API Test Suite")
        print("=" * 60)
        print("")
        
        # Test 1: Basic Gemini API
        basic_test = await test_gemini_basic()
        
        # Test 2: HSE Agent Integration (if basic test passes)
        integration_test = False
        if basic_test:
            integration_test = await test_hse_agent_integration()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"✅ Basic Gemini API:     {'PASS' if basic_test else 'FAIL'}")
        print(f"✅ HSE Agent Integration: {'PASS' if integration_test else 'FAIL'}")
        
        if basic_test and integration_test:
            print("\n🎉 All tests passed! Gemini is ready for HSE system.")
            print("\n📝 Next steps:")
            print("   1. Update your .env file with GEMINI_API_KEY")
            print("   2. Restart the backend: docker-compose restart backend")
            print("   3. Test via API: http://localhost:8000/api/docs")
        else:
            print("\n⚠️  Some tests failed. Check the errors above.")
            if not basic_test:
                print("   - Verify GEMINI_API_KEY in .env file")
                print("   - Check Google AI Studio: https://makersuite.google.com/app/apikey")
        
        print("\n" + "=" * 60)
        return basic_test and integration_test


except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\n📦 Missing dependencies. Please install:")
    print("   pip install google-generativeai python-dotenv")
    sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())