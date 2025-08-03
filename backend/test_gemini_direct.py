import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config.settings import settings
import google.generativeai as genai

print(f"Testing Gemini API...")
print(f"API Key: {settings.gemini_api_key[:10]}...{settings.gemini_api_key[-5:]}")
print(f"Model: {settings.gemini_model}")

try:
    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel(settings.gemini_model)
    
    prompt = "Rispondi in una sola frase: Qual è il rischio principale nel lavorare su un tetto?"
    print(f"\nPrompt: {prompt}")
    
    response = model.generate_content(prompt)
    print(f"\nResponse: {response.text}")
    print("\n✅ Gemini API is working!")
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    print(f"Type: {type(e).__name__}")