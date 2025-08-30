#!/usr/bin/env python3
"""
Script to reprocess document and create chunks in Weaviate
"""
import asyncio
import sys
sys.path.insert(0, '/app')

from app.config.database import SessionLocal
from app.models.document import Document
from app.services.vector_service import VectorService
from app.services.storage_service import StorageService
import docx2txt

async def reprocess_document(doc_id: int):
    """Reprocess document and create chunks"""
    db = SessionLocal()
    vector_service = VectorService()
    storage_service = StorageService()
    
    try:
        # Get document from database
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            print(f"Document {doc_id} not found")
            return
        
        print(f"Processing document: {doc.title} ({doc.document_code})")
        
        # Download and extract content
        file_content = await storage_service.download_file(doc.file_path)
        
        # Extract text based on file type
        if doc.file_path.endswith('.docx'):
            import io
            content = docx2txt.process(io.BytesIO(file_content))
        else:
            content = file_content.decode('utf-8', errors='ignore')
        
        print(f"Extracted {len(content)} characters")
        
        # Create chunks
        chunks = []
        chunk_size = 1000
        for i in range(0, len(content), chunk_size):
            chunk_text = content[i:i+chunk_size]
            chunks.append({
                "content": chunk_text,
                "chunk_index": len(chunks),
                "section_title": f"Chunk {len(chunks) + 1}",
                "relevance_score": 0.5
            })
        
        print(f"Created {len(chunks)} chunks")
        
        # Delete existing chunks if any
        print("Deleting existing chunks...")
        await vector_service.delete_document_chunks(doc.document_code, doc.tenant_id)
        
        # Add chunks to Weaviate
        print("Adding chunks to Weaviate...")
        chunk_ids = await vector_service.add_document_chunks(
            document_id=doc.id,
            document_code=doc.document_code,
            title=doc.title,
            chunks=chunks,
            document_type=doc.document_type,
            category=doc.category,
            tenant_id=doc.tenant_id,
            industry_sectors=doc.industry_sectors or [],
            authority=doc.authority
        )
        
        if chunk_ids:
            # Update document with first chunk ID as vector_id
            doc.vector_id = chunk_ids[0] if chunk_ids else None
            db.commit()
            print(f"✓ Successfully added {len(chunk_ids)} chunks to Weaviate")
            print(f"✓ Updated document vector_id: {doc.vector_id}")
        else:
            print("✗ Failed to add chunks to Weaviate")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    # Process document ID 16
    asyncio.run(reprocess_document(16))