#!/usr/bin/env python3
"""
Test Gemini API limits and response times
"""
import asyncio
import time
import google.generativeai as genai
from app.config.settings import settings

async def test_gemini_api():
    """Test Gemini API with simple requests"""
    
    print("=== Gemini API Test ===")
    print(f"Model: {settings.gemini_model}")
    print(f"API Key configured: {'Yes' if settings.gemini_api_key else 'No'}")
    
    if not settings.gemini_api_key:
        print("❌ GEMINI_API_KEY not configured")
        return
    
    try:
        # Configure Gemini
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(settings.gemini_model)
        
        print(f"\n✅ Gemini configured successfully")
        
        # Test 1: Simple request
        print("\n1. Testing simple request...")
        start_time = time.time()
        
        try:
            response = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: model.generate_content(
                        "Rispondi con una sola parola: 'test'",
                        generation_config=genai.types.GenerationConfig(
                            temperature=0.1,
                            max_output_tokens=10
                        )
                    )
                ),
                timeout=10
            )
            
            duration = time.time() - start_time
            print(f"   ✅ Simple request successful ({duration:.2f}s)")
            print(f"   Response: {response.text}")
            
        except asyncio.TimeoutError:
            print(f"   ❌ Simple request timed out after 10s")
            return
        except Exception as e:
            print(f"   ❌ Simple request failed: {e}")
            if "quota" in str(e).lower() or "limit" in str(e).lower():
                print(f"   🚨 RATE LIMIT DETECTED: {e}")
            return
        
        # Test 2: HSE-style request (like our agents)
        print("\n2. Testing HSE analysis request...")
        start_time = time.time()
        
        hse_prompt = """
Sei un esperto HSE. Analizza questo permesso di lavoro:

PERMESSO: Manutenzione pompa centrifuga
DESCRIZIONE: Sostituzione cuscinetti pompa P-101 in area produzione
TIPO LAVORO: meccanico
DURATA: 4 ore

Fornisci una breve analisi dei rischi e DPI necessari in formato JSON:
{
  "rischi_principali": ["rischio1", "rischio2"],
  "dpi_necessari": ["dpi1", "dpi2"],
  "raccomandazioni": ["raccomandazione1"]
}
"""
        
        try:
            response = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: model.generate_content(
                        hse_prompt,
                        generation_config=genai.types.GenerationConfig(
                            temperature=0.1,
                            max_output_tokens=500
                        )
                    )
                ),
                timeout=30
            )
            
            duration = time.time() - start_time
            print(f"   ✅ HSE request successful ({duration:.2f}s)")
            print(f"   Response length: {len(response.text)} chars")
            
        except asyncio.TimeoutError:
            print(f"   ❌ HSE request timed out after 30s")
            print(f"   🚨 TIMEOUT ISSUE - Gemini is taking too long")
        except Exception as e:
            print(f"   ❌ HSE request failed: {e}")
            if "quota" in str(e).lower() or "limit" in str(e).lower():
                print(f"   🚨 RATE LIMIT DETECTED: {e}")
        
        # Test 3: Multiple rapid requests (rate limit test)
        print("\n3. Testing rate limits (5 rapid requests)...")
        
        for i in range(5):
            try:
                start_time = time.time()
                response = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: model.generate_content(
                            f"Rispondi con 'test {i+1}'",
                            generation_config=genai.types.GenerationConfig(
                                temperature=0.1,
                                max_output_tokens=10
                            )
                        )
                    ),
                    timeout=10
                )
                duration = time.time() - start_time
                print(f"   Request {i+1}: ✅ ({duration:.2f}s)")
                
            except Exception as e:
                print(f"   Request {i+1}: ❌ {e}")
                if "quota" in str(e).lower() or "limit" in str(e).lower():
                    print(f"   🚨 RATE LIMIT HIT ON REQUEST {i+1}")
                    break
            
            # Small delay between requests
            await asyncio.sleep(0.5)
        
        print("\n=== Gemini Test Results ===")
        print("✅ Gemini API is working")
        print("📊 Check response times above")
        print("⚠️  If requests are slow (>10s), consider using gemini-1.5-flash")
        
    except Exception as e:
        print(f"❌ Gemini configuration failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_gemini_api())