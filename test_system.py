#!/usr/bin/env python3
"""
Test script to verify the enhanced system works
"""
import requests
import json

def test_system():
    print("=== Testing Enhanced HSE System ===")
    
    # Test 1: Health check
    print("\n1. Testing system health...")
    try:
        response = requests.get("http://localhost:8000/health")
        health = response.json()
        print(f"   Status: {health.get('status')}")
        print(f"   Database: {health.get('database')}")
        print(f"   Weaviate: {health.get('weaviate')}")
        print(f"   MinIO: {health.get('minio')}")
    except Exception as e:
        print(f"   ✗ Health check failed: {e}")
        return
    
    # Test 2: Authentication
    print("\n2. Testing authentication...")
    try:
        login_data = {
            "username": "admin@acme-corp.com",
            "password": "SuperSecurePass2024!"
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            auth_data = response.json()
            token = auth_data.get("access_token")
            print(f"   ✓ Login successful, token: {token[:20]}...")
        else:
            print(f"   ✗ Login failed: {response.status_code} - {response.text}")
            return
        
    except Exception as e:
        print(f"   ✗ Authentication failed: {e}")
        return
    
    # Test 3: List permits
    print("\n3. Testing permit listing...")
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            "http://localhost:8000/api/v1/permits/",
            headers=headers
        )
        
        if response.status_code == 200:
            permits_data = response.json()
            print(f"   ✓ Found {permits_data.get('total_count', 0)} permits")
        else:
            print(f"   ✗ Permit listing failed: {response.status_code}")
            return
            
    except Exception as e:
        print(f"   ✗ Permit listing failed: {e}")
        return
    
    # Test 4: Analyze a permit (this should work with our improvements)
    print("\n4. Testing permit analysis (enhanced system)...")
    try:
        analysis_data = {
            "force_reanalysis": True
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/permits/1/analyze",
            json=analysis_data,
            headers=headers
        )
        
        print(f"   Response status: {response.status_code}")
        
        if response.status_code == 200:
            analysis_result = response.json()
            print(f"   ✓ Analysis completed successfully")
            print(f"   ✓ Confidence score: {analysis_result.get('confidence_score', 'N/A')}")
            print(f"   ✓ Analysis complete: {analysis_result.get('analysis_complete', 'N/A')}")
            
            # Check for enhanced features
            if 'search_enhancements' in str(analysis_result):
                print(f"   ✓ Enhanced search features detected")
            
        elif response.status_code == 404:
            print(f"   ! Permit not found (need to create test data)")
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            print(f"   ✗ Analysis failed: {response.status_code}")
            print(f"     Error: {error_data}")
            
    except Exception as e:
        print(f"   ✗ Analysis test failed: {e}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_system()