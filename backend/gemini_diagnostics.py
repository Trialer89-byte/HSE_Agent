import os
import sys
import time
import asyncio
import json
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config.settings import settings
import google.generativeai as genai

async def test_gemini_limits():
    print("🔍 Gemini API Diagnostics")
    print("=" * 50)
    
    # Configure Gemini
    try:
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(settings.gemini_model)
        print(f"✅ API Key: {settings.gemini_api_key[:10]}...{settings.gemini_api_key[-5:]}")
        print(f"✅ Model: {settings.gemini_model}")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return

    # Test 1: Simple request
    print("\n📝 Test 1: Simple Request")
    try:
        start_time = time.time()
        response = model.generate_content("Say 'Hello HSE System' in Italian")
        duration = time.time() - start_time
        print(f"✅ Response time: {duration:.2f}s")
        print(f"✅ Response: {response.text}")
    except Exception as e:
        print(f"❌ Simple request failed: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        if hasattr(e, 'response'):
            print(f"❌ HTTP Response: {e.response}")

    # Test 2: Multiple rapid requests (test rate limits)
    print("\n🚀 Test 2: Rate Limit Testing (5 rapid requests)")
    for i in range(5):
        try:
            start_time = time.time()
            response = model.generate_content(f"Request #{i+1}: What is safety?")
            duration = time.time() - start_time
            print(f"✅ Request {i+1}: {duration:.2f}s - {response.text[:50]}...")
        except Exception as e:
            print(f"❌ Request {i+1} failed: {e}")
            print(f"❌ Error type: {type(e).__name__}")
            if "quota" in str(e).lower() or "limit" in str(e).lower():
                print("🚨 RATE LIMIT DETECTED!")
            break
        
        # Small delay between requests
        await asyncio.sleep(0.5)

    # Test 3: Complex HSE prompt (like our agents use)
    print("\n🏗️ Test 3: Complex HSE Analysis Prompt")
    complex_prompt = """
    Sei un esperto HSE (Health, Safety, Environment). Analizza questo permesso di lavoro:

    DETTAGLI PERMESSO:
    - Titolo: Lavoro su tetto
    - Descrizione: Pulire pluviali
    - Tipo: Chimico
    - Durata: 2 ore
    - Ubicazione: Produzione

    Fornisci una risposta in formato JSON con:
    {
        "rischi_identificati": ["rischio1", "rischio2"],
        "dpi_richiesti": ["dpi1", "dpi2"],
        "raccomandazioni": ["raccomandazione1"],
        "livello_rischio": "alto/medio/basso",
        "conformita": "conforme/non_conforme"
    }
    """
    
    try:
        start_time = time.time()
        response = model.generate_content(complex_prompt)
        duration = time.time() - start_time
        print(f"✅ Complex prompt time: {duration:.2f}s")
        print(f"✅ Response length: {len(response.text)} chars")
        print(f"✅ Response preview: {response.text[:200]}...")
        
        # Try to parse as JSON
        try:
            json_response = json.loads(response.text.strip('```json').strip('```'))
            print("✅ Valid JSON response!")
        except:
            print("⚠️ Response is not valid JSON")
            
    except Exception as e:
        print(f"❌ Complex prompt failed: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        if hasattr(e, 'response'):
            print(f"❌ HTTP Status: {getattr(e.response, 'status_code', 'Unknown')}")

    # Test 4: Check quota information
    print("\n📊 Test 4: API Quota Information")
    try:
        # Get model info
        models = genai.list_models()
        for model_info in models:
            if settings.gemini_model in model_info.name:
                print(f"✅ Model found: {model_info.name}")
                print(f"✅ Display name: {model_info.display_name}")
                print(f"✅ Input token limit: {model_info.input_token_limit}")
                print(f"✅ Output token limit: {model_info.output_token_limit}")
                break
    except Exception as e:
        print(f"❌ Could not get model info: {e}")

    print("\n" + "=" * 50)
    print("🏁 Diagnostics Complete")

# Run diagnostics
if __name__ == "__main__":
    asyncio.run(test_gemini_limits())