#!/usr/bin/env python3
"""
Test script to check Weaviate connection and configuration
"""
import weaviate
import requests
import json
from app.config.settings import settings

def test_weaviate_connection():
    """Test Weaviate connection with different methods"""
    
    print("=== Weaviate Connection Test ===")
    print(f"WEAVIATE_URL: {settings.weaviate_url}")
    print(f"WEAVIATE_API_KEY configured: {'Yes' if settings.weaviate_api_key else 'No'}")
    
    # Test 1: Direct HTTP request to check if Weaviate is running
    print("\n1. Testing direct HTTP connection...")
    try:
        response = requests.get(f"{settings.weaviate_url}/v1/.well-known/ready", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ Weaviate is running")
        else:
            print(f"   ✗ Weaviate returned status {response.status_code}")
    except Exception as e:
        print(f"   ✗ HTTP connection failed: {e}")
        return False
    
    # Test 2: Check Weaviate meta endpoint
    print("\n2. Testing Weaviate meta endpoint...")
    try:
        response = requests.get(f"{settings.weaviate_url}/v1/meta", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            meta_data = response.json()
            print(f"   ✓ Weaviate version: {meta_data.get('version', 'unknown')}")
            print(f"   ✓ Modules: {meta_data.get('modules', {}).keys()}")
        else:
            print(f"   ✗ Meta endpoint returned: {response.text}")
    except Exception as e:
        print(f"   ✗ Meta endpoint failed: {e}")
    
    # Test 3: Client connection without auth
    print("\n3. Testing client connection (no auth)...")
    try:
        client = weaviate.Client(
            url=settings.weaviate_url,
            additional_headers={}
        )
        schema = client.schema.get()
        print(f"   ✓ Client connected successfully")
        print(f"   ✓ Schema classes: {[cls.get('class', 'unknown') for cls in schema.get('classes', [])]}")
        return True
    except Exception as e:
        print(f"   ✗ Client connection failed: {e}")
    
    # Test 4: Client connection with API key (if available)
    if settings.weaviate_api_key:
        print("\n4. Testing client connection (with API key)...")
        try:
            auth_config = weaviate.AuthApiKey(api_key=settings.weaviate_api_key)
            client = weaviate.Client(
                url=settings.weaviate_url,
                auth_client_secret=auth_config
            )
            schema = client.schema.get()
            print(f"   ✓ Authenticated client connected")
            print(f"   ✓ Schema classes: {[cls.get('class', 'unknown') for cls in schema.get('classes', [])]}")
            return True
        except Exception as e:
            print(f"   ✗ Authenticated client failed: {e}")
    
    # Test 5: Alternative connection methods
    print("\n5. Testing alternative connection methods...")
    try:
        client = weaviate.Client(
            url=settings.weaviate_url,
            startup_period=10
        )
        ready = client.is_ready()
        print(f"   ✓ Client ready status: {ready}")
        if ready:
            schema = client.schema.get()
            print(f"   ✓ Alternative connection successful")
            return True
    except Exception as e:
        print(f"   ✗ Alternative connection failed: {e}")
    
    return False

def fix_weaviate_schema():
    """Attempt to create the required schema"""
    print("\n=== Schema Setup ===")
    
    try:
        # Try to connect and create schema
        client = weaviate.Client(
            url=settings.weaviate_url,
            additional_headers={}
        )
        
        # Check if HSEDocument class exists
        schema = client.schema.get()
        existing_classes = [cls.get('class', '') for cls in schema.get('classes', [])]
        
        if 'HSEDocument' in existing_classes:
            print("✓ HSEDocument class already exists")
            return True
        
        print("Creating HSEDocument schema...")
        
        hse_schema = {
            "class": "HSEDocument",
            "description": "Documenti normativi e istruzioni operative HSE",
            "properties": [
                {
                    "name": "document_code",
                    "dataType": ["text"],
                    "description": "Codice univoco documento"
                },
                {
                    "name": "title",
                    "dataType": ["text"],
                    "description": "Titolo completo documento"
                },
                {
                    "name": "content",
                    "dataType": ["text"],
                    "description": "Contenuto testuale completo"
                },
                {
                    "name": "content_chunk",
                    "dataType": ["text"],
                    "description": "Chunk semantico di contenuto"
                },
                {
                    "name": "document_type",
                    "dataType": ["text"],
                    "description": "Tipo documento: normativa | istruzione_operativa"
                },
                {
                    "name": "category",
                    "dataType": ["text"],
                    "description": "Categoria HSE"
                },
                {
                    "name": "tenant_id",
                    "dataType": ["int"],
                    "description": "ID tenant per isolamento multi-tenant"
                },
                {
                    "name": "authority",
                    "dataType": ["text"],
                    "description": "Autorità emittente"
                },
                {
                    "name": "ai_keywords",
                    "dataType": ["text[]"],
                    "description": "Keywords estratte da AI"
                },
                {
                    "name": "relevance_score",
                    "dataType": ["number"],
                    "description": "Score rilevanza 0-1"
                }
            ],
            "vectorizer": "text2vec-transformers"
        }
        
        client.schema.create_class(hse_schema)
        print("✓ HSEDocument schema created successfully")
        return True
        
    except Exception as e:
        print(f"✗ Schema creation failed: {e}")
        return False

if __name__ == "__main__":
    success = test_weaviate_connection()
    
    if success:
        print("\n=== Connection Test: PASSED ===")
        fix_weaviate_schema()
    else:
        print("\n=== Connection Test: FAILED ===")
        print("\nPossible solutions:")
        print("1. Check if Weaviate container is running: docker ps")
        print("2. Restart Weaviate: docker-compose restart weaviate")
        print("3. Check Weaviate logs: docker-compose logs weaviate")
        print("4. Verify configuration in docker-compose.simple.yml")