#!/usr/bin/env python3
"""
Test script to verify the analysis endpoint works without blocking
"""
import requests
import json
import time

# Test configuration
BASE_URL = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "HSEAdmin2024!"

def login_and_test():
    """Login and test the analysis endpoint"""
    
    # Step 1: Login to get auth token
    print("🔐 Logging in...")
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    try:
        login_response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json=login_data,
            timeout=10
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return False
            
        token_data = login_response.json()
        token = token_data.get("access_token")
        
        if not token:
            print("❌ No access token received")
            return False
            
        print("✅ Login successful")
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # Step 2: Test permit analysis (should use MockOrchestrator)
    print("\n🔍 Testing permit analysis...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    analysis_data = {
        "force_reanalysis": True,
        "analysis_scope": ["content", "risk", "compliance", "dpi"]
    }
    
    start_time = time.time()
    
    try:
        # Use a longer timeout but expect it to complete much faster
        analysis_response = requests.post(
            f"{BASE_URL}/api/v1/permits/1/analyze",
            json=analysis_data,
            headers=headers,
            timeout=60  # 60 second timeout, but should complete in <5 seconds
        )
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        print(f"⏱️  Analysis completed in {elapsed:.2f} seconds")
        
        if analysis_response.status_code == 200:
            print("✅ Analysis successful!")
            
            # Parse response to check if it's using MockOrchestrator
            result = analysis_response.json()
            ai_version = result.get("ai_version", "Unknown")
            analysis_id = result.get("analysis_id", "Unknown")
            confidence = result.get("confidence_score", 0.0)
            
            print(f"📊 Analysis ID: {analysis_id}")
            print(f"🤖 AI Version: {ai_version}")
            print(f"📈 Confidence: {confidence:.2f}")
            
            # Check if it's mock analysis
            if "Mock" in ai_version:
                print("✅ Using MockOrchestrator as expected")
            else:
                print(f"⚠️  Using different orchestrator: {ai_version}")
                
            return True
            
        else:
            print(f"❌ Analysis failed: {analysis_response.status_code}")
            print(f"Response: {analysis_response.text}")
            return False
            
    except requests.exceptions.Timeout:
        end_time = time.time()
        elapsed = end_time - start_time
        print(f"❌ Analysis timed out after {elapsed:.2f} seconds")
        print("💡 This suggests the blocking issue still exists")
        return False
        
    except Exception as e:
        end_time = time.time()
        elapsed = end_time - start_time
        print(f"❌ Analysis error after {elapsed:.2f} seconds: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing HSE Agent Analysis Endpoint")
    print("=" * 50)
    
    success = login_and_test()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All tests passed! The blocking issue appears to be fixed.")
    else:
        print("❌ Tests failed. The blocking issue may still exist.")