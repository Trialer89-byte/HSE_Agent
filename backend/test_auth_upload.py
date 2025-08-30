#!/usr/bin/env python3
"""
Script to test document upload with authentication
"""
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
EMAIL = "admin@example.com"
PASSWORD = "admin123"  # Update with correct password

def login():
    """Login and get token"""
    url = f"{BASE_URL}/api/v1/auth/login"
    data = {
        "email": EMAIL,
        "password": PASSWORD
    }
    
    response = requests.post(url, json=data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"✓ Login successful, token: {token[:20]}...")
        return token
    else:
        print(f"✗ Login failed: {response.status_code}")
        print(response.text)
        return None

def upload_document(token, file_path):
    """Upload document with authentication"""
    url = f"{BASE_URL}/api/v1/documents/upload"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    with open(file_path, 'rb') as f:
        files = {
            'file': (file_path, f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        }
        data = {
            'title': 'Permesso di Lavoro',
            'document_type': 'istruzione_operativa',
            'category': 'sicurezza'
        }
        
        response = requests.post(url, headers=headers, files=files, data=data)
        
        if response.status_code == 200:
            print(f"✓ Document uploaded successfully")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"✗ Upload failed: {response.status_code}")
            print(response.text)

if __name__ == "__main__":
    # Step 1: Login
    token = login()
    
    if token:
        # Step 2: Upload document
        upload_document(token, "HSE2.08.01 Permesso di Lavoro.docx")
    else:
        print("\nAlternative: Use test endpoint without authentication:")
        print("curl -X POST http://localhost:8000/api/v1/test/documents/upload \\")
        print('  -F "file=@HSE2.08.01 Permesso di Lavoro.docx" \\')
        print('  -F "title=Permesso di Lavoro" \\')
        print('  -F "document_type=istruzione_operativa" \\')
        print('  -F "tenant_id=1"')