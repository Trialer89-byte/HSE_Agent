#!/usr/bin/env python3
"""
Script to manually sync HSE-4064 document from PostgreSQL to Weaviate
"""
import sys
import os
sys.path.append('backend')

import asyncio
from app.database import get_db
from app.models.document import Document
from app.services.vector_service import VectorService
from app.services.document_service import DocumentService
from sqlalchemy.orm import Session


async def sync_document_to_weaviate(document_id: int):
    """
    Manually sync a document from PostgreSQL to Weaviate
    """
    db = next(get_db())
    vector_service = VectorService()
    document_service = DocumentService(db)
    
    try:
        # Get document from PostgreSQL
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            print(f"❌ Document with ID {document_id} not found in PostgreSQL")
            return False
        
        print(f"✅ Found document: {document.title} (Code: {document.document_code})")
        
        # Check if document exists in Weaviate
        search_results = await vector_service.hybrid_search(
            query=document.title,
            filters={"tenant_id": document.tenant_id, "document_code": document.document_code},
            limit=1,
            threshold=0.0
        )
        
        if search_results:
            print(f"⚠️ Document already exists in Weaviate with {len(search_results)} chunks")
            return True
        
        print("📝 Document not found in Weaviate. Starting sync process...")
        
        # Read the document file content
        file_path = document.file_path
        if not file_path or not os.path.exists(file_path.replace('/app/', '')):
            print(f"❌ Document file not found: {file_path}")
            return False
        
        # Extract content from file (simplified for text files)
        content = ""
        try:
            with open(file_path.replace('/app/', ''), 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return False
        
        if not content.strip():
            print("❌ Document content is empty")
            return False
            
        print(f"✅ Extracted content: {len(content)} characters")
        
        # Create semantic chunks
        chunks = await document_service._create_semantic_chunks(
            content, document.document_type, document.document_code
        )
        
        if not chunks:
            print("❌ No chunks created from document")
            return False
            
        print(f"✅ Created {len(chunks)} semantic chunks")
        
        # Add chunks to Weaviate
        try:
            chunk_ids = await vector_service.add_document_chunks(
                document_id=document.id,
                document_code=document.document_code,
                title=document.title,
                chunks=chunks,
                document_type=document.document_type,
                category=document.category or "generale",
                tenant_id=document.tenant_id,
                industry_sectors=document.industry_sectors or [],
                authority=document.authority
            )
            
            if chunk_ids:
                print(f"✅ Successfully added {len(chunk_ids)} chunks to Weaviate")
                
                # Update document with vector_id
                document.vector_id = chunk_ids[0]
                if chunks:
                    avg_relevance = sum(chunk.get("relevance_score", 0.0) for chunk in chunks) / len(chunks)
                    document.relevance_score = round(avg_relevance, 2)
                db.commit()
                
                # Verify the document is searchable
                search_results = await vector_service.hybrid_search(
                    query=document.title,
                    filters={"tenant_id": document.tenant_id, "document_code": document.document_code},
                    limit=1,
                    threshold=0.0
                )
                
                if search_results:
                    print(f"🎯 Document verified in Weaviate: {len(search_results)} chunks found")
                    return True
                else:
                    print("❌ Document not searchable in Weaviate after sync")
                    return False
            else:
                print("❌ No chunks were added to Weaviate")
                return False
                
        except Exception as vector_error:
            print(f"❌ Vector processing failed: {str(vector_error)}")
            return False
            
    except Exception as e:
        print(f"❌ Sync failed: {str(e)}")
        return False
    finally:
        db.close()


async def main():
    """
    Main function to sync HSE-4064 document
    """
    print("🔄 Starting HSE-4064 document sync to Weaviate...")
    
    # Document ID 10 is the HSE-4064 working height document
    success = await sync_document_to_weaviate(10)
    
    if success:
        print("✅ Document sync completed successfully!")
    else:
        print("❌ Document sync failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())