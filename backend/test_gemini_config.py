#!/usr/bin/env python3
"""
Test script to verify Gemini API configuration and connectivity
"""
import sys
sys.path.append('/app')

import asyncio
from app.config.settings import settings

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

async def test_gemini_config():
    """Test Gemini API configuration"""
    print("🧪 Testing Gemini API Configuration")
    print("=" * 50)
    
    if not GENAI_AVAILABLE:
        print("❌ google-generativeai library not available")
        print("   Run: pip install google-generativeai")
        return False
    
    # Check API key
    api_key = settings.gemini_api_key
    if not api_key:
        print("❌ GEMINI_API_KEY not configured")
        print("   Set GEMINI_API_KEY in your environment or .env file")
        return False
    
    print(f"✅ API Key configured: {api_key[:8]}...{api_key[-4:]}")
    
    # Check model configuration
    model_name = settings.gemini_model
    print(f"✅ Model configured: {model_name}")
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        
        print("✅ Gemini client initialized successfully")
        
        # Test simple API call
        print("\n🔍 Testing API connectivity...")
        
        response = await asyncio.to_thread(
            model.generate_content,
            "Rispondi brevemente: Cos'è la sicurezza sul lavoro in Italia?"
        )
        
        if response and response.text:
            print("✅ API call successful!")
            print(f"📝 Response preview: {response.text[:100]}...")
            return True
        else:
            print("❌ API call failed - no response")
            return False
            
    except Exception as e:
        print(f"❌ Gemini API error: {str(e)}")
        
        # Check for common errors
        if "API_KEY_INVALID" in str(e):
            print("💡 Solution: Check your GEMINI_API_KEY is correct")
        elif "QUOTA_EXCEEDED" in str(e):
            print("💡 Solution: Check your API quota and billing")
        elif "MODEL_NOT_FOUND" in str(e):
            print("💡 Solution: Check the model name is correct")
        
        return False

async def test_settings():
    """Test all relevant settings"""
    print("\n⚙️  Current Settings:")
    print(f"   AI Provider: {settings.ai_provider}")
    print(f"   Gemini Model: {settings.gemini_model}")
    print(f"   Environment: {settings.environment}")
    
    # Check if running in Docker
    import os
    if os.path.exists('/.dockerenv'):
        print("   Runtime: Docker Container")
    else:
        print("   Runtime: Local Development")

async def main():
    print("Gemini API Configuration Test")
    print("=" * 50)
    
    await test_settings()
    success = await test_gemini_config()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Gemini API is configured and working!")
        print("\nYou can now use:")
        print('   {"orchestrator": "ai"} for full Gemini analysis')
        print('   {"orchestrator": "fast"} for quick Gemini analysis')
        print('   {"orchestrator": "mock"} for instant test results')
    else:
        print("❌ Gemini API configuration has issues")
        print("   Fix the issues above and test again")

if __name__ == "__main__":
    asyncio.run(main())