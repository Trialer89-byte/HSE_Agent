#!/usr/bin/env python
"""
Script to reindex a document in Weaviate
"""
import sys
import os
sys.path.insert(0, '/app')

import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.document import Document
from app.services.vector_service import VectorService
from app.config.settings import settings

async def reindex_document(document_id: int):
    # Create database connection
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Find document
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            print(f'Document ID {document_id} not found')
            return False
            
        print(f'Found document: {document.title}')
        print(f'Type: {document.document_type}')
        print(f'Tenant ID: {document.tenant_id}')
        print(f'File path: {document.file_path}')
        print(f'Content summary: {document.content_summary[:100] if document.content_summary else "No summary"}')
        
        # Initialize vector service
        vector_service = VectorService()
        print('[VectorService] Initialized')
        
        # Read content from file or use content_summary
        content = None
        if document.file_path:
            # Try to read from MinIO
            try:
                from app.services.storage_service import StorageService
                storage_service = StorageService()
                content = await storage_service.get_file_content(document.file_path)
                if isinstance(content, bytes):
                    content = content.decode('utf-8', errors='ignore')
                print(f'Read {len(content)} characters from file storage')
            except Exception as e:
                print(f'Could not read from file storage: {e}')
        
        if not content and document.content_summary:
            content = document.content_summary
            print(f'Using content_summary ({len(content)} characters)')
        
        # Create chunks from content
        if content:
            # Simple chunking for testing
            chunk_size = 2000
            chunks = []
            
            for i in range(0, len(content), chunk_size):
                chunk_content = content[i:i+chunk_size]
                chunks.append({
                    'content': chunk_content,
                    'chunk_index': i // chunk_size,
                    'section_title': f'Sezione {i // chunk_size + 1}',
                    'ai_keywords': ['sicurezza', 'lavoro', 'D.Lgs', '81/2008', 'HSE'],
                    'relevance_score': 0.9
                })
            
            print(f'Created {len(chunks)} chunks from document')
            
            # Add to Weaviate
            print('Adding chunks to Weaviate...')
            result = await vector_service.add_document_chunks(
                document_id=document.id,
                document_code=document.document_code or f'DOC_{document.id}',
                title=document.title,
                chunks=chunks,
                document_type=document.document_type,
                category=document.category or 'generale',
                tenant_id=document.tenant_id,
                industry_sectors=document.industry_sectors or [],
                authority=document.authority
            )
            
            print(f'Successfully added {len(result)} chunks to Weaviate')
            
            # Test search
            print('\nTesting search...')
            search_results = await vector_service.hybrid_search(
                query='sicurezza lavoro',
                filters={'tenant_id': document.tenant_id},
                limit=5,
                threshold=0.1
            )
            
            print(f'Test search found {len(search_results)} results')
            if search_results:
                print('First result:', search_results[0].get('title', 'No title'))
            
            return True
            
        else:
            print('ERROR: Document has no content to index')
            return False
            
    except Exception as e:
        import traceback
        print(f'ERROR: {e}')
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == '__main__':
    document_id = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    print(f'=== Reindexing document ID {document_id} ===')
    success = asyncio.run(reindex_document(document_id))
    print(f'\n=== Reindexing {"SUCCESSFUL" if success else "FAILED"} ===')
    sys.exit(0 if success else 1)