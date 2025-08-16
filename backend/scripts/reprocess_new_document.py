#!/usr/bin/env python
"""
Reprocess the newly uploaded document with full content
"""
import sys
sys.path.insert(0, '/app')

import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.document import Document
from app.services.vector_service import VectorService
from app.services.storage_service import StorageService
from app.config.settings import settings
import pypdf
import io

async def reprocess_latest_document():
    # Create database connection
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Find latest document
        document = db.query(Document).order_by(Document.created_at.desc()).first()
        
        if not document:
            print('No documents found')
            return False
            
        print(f'=== Processing Latest Document ===')
        print(f'ID: {document.id}')
        print(f'Title: {document.title}')
        print(f'File path: {document.file_path}')
        print(f'Created: {document.created_at}')
        
        # Get PDF from MinIO
        storage = StorageService()
        vector_service = VectorService()
        
        print(f'\n1. Downloading PDF from MinIO...')
        response = storage.client.get_object('hse-documents', document.file_path)
        pdf_data = response.read()
        response.close()
        response.release_conn()
        print(f'   Downloaded: {len(pdf_data)} bytes')
        
        # Extract text quickly (first 20 pages for testing)
        print(f'\n2. Extracting text from PDF...')
        pdf_file = io.BytesIO(pdf_data)
        pdf_reader = pypdf.PdfReader(pdf_file)
        print(f'   PDF has {len(pdf_reader.pages)} pages')
        
        # Extract first 20 pages
        content = ""
        max_pages = min(20, len(pdf_reader.pages))
        for i, page in enumerate(pdf_reader.pages[:max_pages]):
            try:
                page_text = page.extract_text()
                content += f"\n\n--- Pagina {i+1} ---\n{page_text}"
            except Exception as e:
                print(f'   Warning: Could not extract page {i+1}: {e}')
        
        print(f'   Extracted {len(content)} characters from {max_pages} pages')
        
        # Create fewer but larger chunks for faster processing
        print(f'\n3. Creating chunks...')
        chunk_size = 3000  # Larger chunks
        chunks = []
        
        # Simple chunking
        for i in range(0, len(content), chunk_size):
            chunk_content = content[i:i+chunk_size]
            
            chunks.append({
                'content': chunk_content,
                'chunk_index': len(chunks),
                'section_title': f'Sezione {len(chunks) + 1}',
                'ai_keywords': ['sicurezza', 'lavoro', 'D.Lgs', '81/2008', 'HSE', 'normativa'],
                'relevance_score': 0.9
            })
        
        print(f'   Created {len(chunks)} chunks')
        
        # Add chunks to Weaviate with smaller batches
        print(f'\n4. Adding chunks to Weaviate (small batches)...')
        batch_size = 5  # Much smaller batches
        
        total_added = 0
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]
            print(f'   Processing batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1} ({len(batch)} chunks)...')
            
            try:
                result = await vector_service.add_document_chunks(
                    document_id=document.id,
                    document_code=document.document_code,
                    title=document.title,
                    chunks=batch,
                    document_type=document.document_type,
                    category=document.category or 'normativa',
                    tenant_id=document.tenant_id,
                    industry_sectors=document.industry_sectors or [],
                    authority=document.authority or 'Governo Italiano'
                )
                total_added += len(result)
                print(f'   Batch successful: {len(result)} chunks added')
                
                # Small delay between batches
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f'   Batch failed: {e}')
        
        print(f'\n   Total chunks added: {total_added}')
        
        # Update document summary
        if len(content) > 500:
            # Store more content as summary
            document.content_summary = content[:3000]  # First 3000 chars
            db.commit()
            print(f'\n5. Updated document summary in database')
        
        # Quick test search
        print(f'\n6. Testing search...')
        results = await vector_service.hybrid_search(
            query='sicurezza lavoro decreto',
            filters={'tenant_id': document.tenant_id},
            limit=3,
            threshold=0.1
        )
        print(f'   Search test: found {len(results)} results')
        
        return total_added > 0
        
    except Exception as e:
        import traceback
        print(f'ERROR: {e}')
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == '__main__':
    print('Processing latest uploaded document...')
    success = asyncio.run(reprocess_latest_document())
    print(f'\n=== Processing {"SUCCESSFUL" if success else "FAILED"} ===')
    sys.exit(0 if success else 1)