"""
Test script to upload a document and monitor the process
"""
import asyncio
import httpx
import time
import json

async def test_document_upload():
    """Test document upload with monitoring"""
    
    print("=" * 60)
    print("TEST: Upload documento con debug logging")
    print("=" * 60)
    
    # Create a simple test file
    test_content = """
    DECRETO LEGISLATIVO TEST
    
    Articolo 1 - Test di sicurezza
    Questo è un documento di test per verificare il sistema di upload.
    
    Articolo 2 - Procedure di sicurezza
    Le procedure di sicurezza devono essere rispettate durante i lavori.
    
    Articolo 3 - DPI obbligatori
    Casco, guanti, scarpe antinfortunistiche sono obbligatori.
    """.strip()
    
    print(f"1. Creazione file di test ({len(test_content)} caratteri)")
    
    async with httpx.AsyncClient(timeout=180.0) as client:
        # Login
        print("\n2. Login...")
        login_response = await client.post(
            "http://localhost:8000/api/v1/auth/login",
            json={"username": "admin_demo_company", "password": "admin123"}
        )
        
        if login_response.status_code != 200:
            print(f"   ❌ Login fallito: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            return
        
        token = login_response.json()["access_token"]
        print("   [OK] Login riuscito")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Upload document
        print("\n3. Upload documento...")
        
        files = {
            "file": ("test_decreto.txt", test_content.encode(), "text/plain")
        }
        
        data = {
            "title": "Test Decreto Sicurezza",
            "document_type": "normativa",
            "category": "sicurezza",
            "subcategory": "test",
            "authority": "Test Authority",
            "scope": "tenant",
            "industry_sectors": '["generale"]',
            "force_reload": "true"  # Force reload to bypass hash check
        }
        
        upload_response = await client.post(
            "http://localhost:8000/api/v1/documents/upload",
            files=files,
            data=data,
            headers=headers
        )
        
        if upload_response.status_code != 200:
            print(f"   [X] Upload fallito: {upload_response.status_code}")
            print(f"   Response: {upload_response.text}")
            return
        
        upload_result = upload_response.json()
        task_id = upload_result["task_id"]
        print(f"   [OK] Upload avviato, task_id: {task_id}")
        
        # Monitor progress
        print("\n4. Monitoraggio progresso...")
        max_wait = 120  # 2 minutes max
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            status_response = await client.get(
                f"http://localhost:8000/api/v1/documents/upload/status/{task_id}",
                headers=headers
            )
            
            if status_response.status_code != 200:
                print(f"   [X] Errore status: {status_response.status_code}")
                break
            
            status = status_response.json()
            
            print(f"   Status: {status['status']} | Progress: {status['progress']}% | Message: {status['message']}")
            
            if status["status"] in ["completed", "failed"]:
                print(f"\n   [FINALE] {status['status']}")
                if status["status"] == "completed":
                    print(f"   Document ID: {status.get('document_id', 'N/A')}")
                else:
                    print(f"   [X] Error: {status.get('error', 'Unknown error')}")
                break
            
            await asyncio.sleep(3)  # Check every 3 seconds
        else:
            print(f"   [!] Timeout dopo {max_wait} secondi")
        
        # Final status
        final_status = status_response.json()
        
        print(f"\n5. Risultato finale:")
        print(f"   Status: {final_status['status']}")
        print(f"   Document ID: {final_status.get('document_id', 'N/A')}")
        print(f"   Error: {final_status.get('error', 'N/A')}")
        
        # If successful, check document in database
        if final_status["status"] == "completed" and final_status.get("document_id"):
            doc_id = final_status["document_id"]
            print(f"\n6. Verifica documento {doc_id} in database...")
            
            # Check PostgreSQL
            import subprocess
            try:
                pg_result = subprocess.run([
                    "docker", "exec", "hse-agent-postgres", 
                    "psql", "-U", "hse_user", "-d", "hse_agent", 
                    "-c", f"SELECT id, document_code, title, vector_id FROM documents WHERE id = {doc_id};"
                ], capture_output=True, text=True, timeout=30)
                
                if pg_result.returncode == 0:
                    print("   [OK] PostgreSQL:")
                    print("   " + pg_result.stdout.replace('\n', '\n   '))
                else:
                    print(f"   [X] PostgreSQL error: {pg_result.stderr}")
            except Exception as e:
                print(f"   [X] PostgreSQL check failed: {e}")
        
        print("\n" + "=" * 60)
        print("TEST COMPLETATO")
        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_document_upload())