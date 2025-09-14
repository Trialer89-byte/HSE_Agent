#!/usr/bin/env python3
"""
Simple test script to verify the fixed document upload flow
"""
import requests
import json
import time
from pathlib import Path


def test_upload_flow():
    """Test the complete document upload and sync flow"""
    
    print("Testing Fixed Document Upload Flow")
    print("="*50)
    
    # Test document content
    test_doc_content = """HSE-TEST-002 ISTRUZIONE OPERATIVA - UPLOAD TEST

OGGETTO: Test sincronizzazione migliorata

1. SCOPO
Verificare funzionamento upload con retry e fallback.

2. DPI RICHIESTI
- Casco di protezione EN 397
- Imbracatura anticaduta EN 361
- Calzature antinfortunistiche

3. PROCEDURA SICUREZZA
3.1 Controllo DPI prima uso
3.2 Verifica punti ancoraggio
3.3 Mantenimento collegamento sicurezza
3.4 Controlli post-lavoro

4. EMERGENZE
In caso incidente:
- Allertare soccorsi (118)
- Prestare primo soccorso
- Non spostare infortunato

Data: 2025-09-13
Versione: TEST v1.0"""
    
    # Create test file
    test_file = Path("test_simple_upload.txt")
    test_file.write_text(test_doc_content, encoding='utf-8')
    
    try:
        # Step 1: Login
        print("1. Authenticating...")
        login_response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            json={"username": "admin", "password": "HSEAdmin2024!"}
        )
        
        if login_response.status_code != 200:
            print(f"Login failed: {login_response.text}")
            return False
        
        token = login_response.json().get("access_token")
        print("Authentication successful")
        
        # Step 2: Upload document
        print("\n2. Uploading document...")
        
        with open(test_file, 'rb') as f:
            files = {'file': ('test_simple_upload.txt', f, 'text/plain')}
            data = {
                'title': 'HSE-TEST-002 Simple Upload Test',
                'document_type': 'istruzione_operativa',
                'category': 'sicurezza',
                'force_reload': 'true'
            }
            
            upload_response = requests.post(
                "http://localhost:8000/api/v1/documents/upload",
                files=files,
                data=data,
                headers={"Authorization": f"Bearer {token}"}
            )
        
        if upload_response.status_code != 200:
            print(f"Upload failed: {upload_response.text}")
            return False
        
        task_id = upload_response.json().get("task_id")
        print(f"Upload started, task ID: {task_id}")
        
        # Step 3: Monitor progress
        print("\n3. Monitoring progress...")
        
        for i in range(24):  # 2 minutes max (24 * 5 seconds)
            time.sleep(5)
            
            status_response = requests.get(
                f"http://localhost:8000/api/v1/documents/upload/status/{task_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if status_response.status_code != 200:
                continue
            
            status_data = status_response.json()
            status = status_data.get("status")
            progress = status_data.get("progress", 0)
            
            print(f"   Status: {status}, Progress: {progress}%")
            
            if status == "completed":
                verification = status_data.get("verification", {})
                postgres_ok = verification.get("postgres_verified", False)
                weaviate_ok = verification.get("weaviate_verified", False)
                
                print(f"\nUpload completed!")
                print(f"PostgreSQL: {'OK' if postgres_ok else 'FAILED'}")
                print(f"Weaviate: {'OK' if weaviate_ok else 'FAILED'}")
                
                return postgres_ok and weaviate_ok
            
            elif status == "failed":
                error = status_data.get("error", "Unknown")
                print(f"Upload failed: {error}")
                return False
        
        print("Upload timeout")
        return False
        
    except Exception as e:
        print(f"Test failed: {e}")
        return False
    
    finally:
        if test_file.exists():
            test_file.unlink()


def main():
    """Main test function"""
    print("Starting upload flow test...")
    success = test_upload_flow()
    
    print("\n" + "="*50)
    if success:
        print("SUCCESS: Fixed upload flow works correctly!")
        print("Both PostgreSQL and Weaviate sync completed")
    else:
        print("FAILED: Upload flow still has issues")
        print("Check backend logs for details")
    print("="*50)


if __name__ == "__main__":
    main()