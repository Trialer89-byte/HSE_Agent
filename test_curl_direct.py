#!/usr/bin/env python3
"""
Test the system with direct curl
"""
import subprocess
import json
import time

# Test with X-API-Key
print("=== Testing AutoGen Analysis with Citation Fix ===")

# Run curl command
curl_cmd = [
    'curl', '-X', 'POST',
    'http://localhost:8000/api/v1/permits/5/analyze',
    '-H', 'Content-Type: application/json',
    '-H', 'X-API-Key: test-key-123',
    '-d', '{"ai_version": "autogen", "analysis_type": "comprehensive"}',
    '-s'  # Silent mode
]

result = subprocess.run(curl_cmd, capture_output=True, text=True)

print(f"Response received")

# Parse response
try:
    response = json.loads(result.stdout)
    
    if 'error' not in response:
        print("\n[SUCCESS] Analysis successful!")
        print(f"  Processing time: {response.get('processing_time')}s")
        print(f"  Confidence score: {response.get('confidence_score')}")
        print(f"  Agents involved: {response.get('agents_involved')}")
        
        # Check citations
        citations = response.get('citations', {})
        normative = citations.get('normative_framework', [])
        print(f"\n  Citations found: {len(normative)}")
        for citation in normative:
            if isinstance(citation, dict):
                doc_info = citation.get('document_info', {})
                print(f"  - {doc_info.get('title')} ({doc_info.get('type')})")
            else:
                print(f"  - ERROR: Citation is not a dict: {type(citation)} - {citation}")
                
        # Check key findings
        exec_summary = response.get('executive_summary', {})
        findings = exec_summary.get('key_findings', [])
        print(f"\n  Key findings: {len(findings)} items")
        for finding in findings[:3]:
            print(f"  - {finding}")
            
    else:
        error = response.get('error', {})
        print(f"\n[ERROR] Error: {error.get('message', 'Unknown error')}")
        print(f"  Full error: {json.dumps(error, indent=2)}")
        
except Exception as e:
    print(f"\n[ERROR] Failed to parse response: {e}")
    print(f"  Raw output: {result.stdout}")
    if result.stderr:
        print(f"  Stderr: {result.stderr}")