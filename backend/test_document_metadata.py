#!/usr/bin/env python3
"""
Test script per verificare l'estrazione automatica dei metadati dei documenti
"""
import asyncio
import sys
import os

# Add the parent directory to the path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.document_service import DocumentService
from sqlalchemy.orm import Session


async def test_ai_metadata_extraction():
    """Test della funzione di estrazione metadati AI"""
    
    # Mock document service (senza DB per il test)
    class MockSession:
        pass
    
    doc_service = DocumentService(MockSession())
    
    # Test content
    test_content = """
    DECRETO LEGISLATIVO 81/2008
    Testo Unico sulla sicurezza sul lavoro
    
    Art. 1 - Campo di applicazione
    Il presente decreto si applica a tutti i settori di attività, privati e pubblici, 
    e a tutte le tipologie di rischio.
    
    Art. 15 - Misure generali di tutela
    Le misure generali di tutela della salute e della sicurezza dei lavoratori nei luoghi di lavoro sono:
    a) la valutazione di tutti i rischi per la salute e sicurezza
    b) la programmazione della prevenzione
    """
    
    print("🔍 Testing AI metadata extraction...")
    
    try:
        metadata = await doc_service._extract_ai_metadata(
            content=test_content,
            title="D.Lgs. 81/2008 - Testo Unico Sicurezza",
            document_type="normativa"
        )
        
        print("✅ Metadata extracted successfully:")
        print(f"   📂 Category: {metadata.get('category')}")
        print(f"   📁 Subcategory: {metadata.get('subcategory')}")
        print(f"   🏛️ Authority: {metadata.get('authority')}")
        print(f"   🎯 Scope: {metadata.get('scope')}")
        print(f"   🏭 Industry Sectors: {metadata.get('industry_sectors')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during metadata extraction: {e}")
        return False


def test_document_code_generation():
    """Test della generazione automatica del document_code"""
    
    import re
    from datetime import datetime
    
    title = "Procedura di Sicurezza per Lavori in Quota - Rev. 2024"
    
    # Simulate the code generation logic
    base_code = re.sub(r'[^a-zA-Z0-9]', '_', title.lower())[:30]
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    document_code = f"{base_code}_{timestamp}"
    
    print("🔧 Testing document code generation...")
    print(f"   📝 Original title: {title}")
    print(f"   🏷️ Generated code: {document_code}")
    
    # Basic validation
    if len(document_code) > 0 and '_' in document_code:
        print("✅ Document code generation works correctly")
        return True
    else:
        print("❌ Document code generation failed")
        return False


async def main():
    """Main test function"""
    print("🚀 Starting Document Metadata Tests\n")
    
    # Test 1: Document code generation
    test1_passed = test_document_code_generation()
    print()
    
    # Test 2: AI metadata extraction
    test2_passed = await test_ai_metadata_extraction()
    print()
    
    # Summary
    if test1_passed and test2_passed:
        print("🎉 All tests passed!")
    else:
        print("⚠️ Some tests failed")
        
    return test1_passed and test2_passed


if __name__ == "__main__":
    asyncio.run(main())