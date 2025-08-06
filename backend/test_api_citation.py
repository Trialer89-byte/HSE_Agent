#!/usr/bin/env python3
"""
Test the API with citation fix
"""
import requests
import json

# Login to get token
login_url = "http://localhost:8000/api/v1/auth/login"
login_data = {
    "username": "admin",
    "password": "admin123"
}

response = requests.post(login_url, json=login_data)
if response.status_code != 200:
    print(f"Login failed: {response.text}")
    exit(1)

token = response.json()["access_token"]
print(f"✓ Authenticated successfully")

# Test AutoGen analysis
analyze_url = "http://localhost:8000/api/v1/permits/5/analyze"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
payload = {
    "ai_version": "autogen",
    "analysis_type": "comprehensive"
}

print("\n=== Testing AutoGen Analysis with Citation Fix ===")
response = requests.post(analyze_url, headers=headers, json=payload)

if response.status_code == 200:
    result = response.json()
    print(f"✓ Analysis successful!")
    print(f"  Processing time: {result.get('processing_time')}s")
    print(f"  Confidence score: {result.get('confidence_score')}")
    print(f"  Agents involved: {result.get('agents_involved')}")
    
    # Check citations
    citations = result.get('citations', {})
    normative = citations.get('normative_framework', [])
    print(f"\n  Citations found: {len(normative)}")
    for citation in normative:
        if isinstance(citation, dict):
            doc_info = citation.get('document_info', {})
            print(f"  - {doc_info.get('title')} ({doc_info.get('type')})")
        else:
            print(f"  - ERROR: Citation is not a dict: {type(citation)}")
            
    # Check key findings
    exec_summary = result.get('executive_summary', {})
    print(f"\n  Key findings: {exec_summary.get('key_findings', [])}")
    print(f"  Critical issues: {exec_summary.get('critical_issues')}")
    
else:
    print(f"✗ Analysis failed with status {response.status_code}")
    print(f"  Error: {response.text}")