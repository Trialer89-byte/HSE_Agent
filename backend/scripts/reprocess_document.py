#!/usr/bin/env python
"""
Reprocess document with full text extraction and chunking
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

async def reprocess_document(document_id: int):
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
            
        print(f'=== Reprocessing Document ===')
        print(f'ID: {document.id}')
        print(f'Title: {document.title}')
        print(f'File path: {document.file_path}')
        
        # Get PDF from MinIO
        storage = StorageService()
        vector_service = VectorService()
        
        print('\n1. Downloading PDF from MinIO...')
        response = storage.client.get_object('hse-documents', document.file_path)
        pdf_data = response.read()
        response.close()
        response.release_conn()
        print(f'   Downloaded: {len(pdf_data)} bytes')
        
        # Extract text
        print('\n2. Extracting text from PDF...')
        pdf_file = io.BytesIO(pdf_data)
        pdf_reader = pypdf.PdfReader(pdf_file)
        print(f'   PDF has {len(pdf_reader.pages)} pages')
        
        # Extract all text (limit to first 100 pages for performance)
        content = ""
        max_pages = min(100, len(pdf_reader.pages))
        for i, page in enumerate(pdf_reader.pages[:max_pages]):
            try:
                page_text = page.extract_text()
                content += f"\n\n--- Pagina {i+1} ---\n{page_text}"
                if i % 10 == 0:
                    print(f'   Processed {i+1}/{max_pages} pages...')
            except Exception as e:
                print(f'   Warning: Could not extract page {i+1}: {e}')
        
        print(f'   Extracted {len(content)} characters from {max_pages} pages')
        
        # Create semantic chunks
        print('\n3. Creating semantic chunks...')
        chunk_size = 2000  # Characters per chunk
        overlap = 200      # Overlap between chunks
        chunks = []
        
        # Smart chunking based on content
        sections = content.split('\n\n')
        current_chunk = ""
        chunk_index = 0
        
        for section in sections:
            if len(current_chunk) + len(section) < chunk_size:
                current_chunk += "\n\n" + section
            else:
                if current_chunk:
                    # Extract keywords from chunk
                    keywords = extract_keywords(current_chunk)
                    
                    chunks.append({
                        'content': current_chunk.strip(),
                        'chunk_index': chunk_index,
                        'section_title': f'Sezione {chunk_index + 1}',
                        'ai_keywords': keywords,
                        'relevance_score': 0.9
                    })
                    chunk_index += 1
                    
                    # Start new chunk with overlap
                    if len(current_chunk) > overlap:
                        current_chunk = current_chunk[-overlap:] + "\n\n" + section
                    else:
                        current_chunk = section
        
        # Add last chunk
        if current_chunk:
            chunks.append({
                'content': current_chunk.strip(),
                'chunk_index': chunk_index,
                'section_title': f'Sezione {chunk_index + 1}',
                'ai_keywords': extract_keywords(current_chunk),
                'relevance_score': 0.9
            })
        
        print(f'   Created {len(chunks)} chunks')
        
        # Clear existing chunks from Weaviate (optional)
        # This would require implementing a delete method
        
        # Add chunks to Weaviate
        print('\n4. Adding chunks to Weaviate...')
        result = await vector_service.add_document_chunks(
            document_id=document.id,
            document_code=document.document_code,
            title=document.title,
            chunks=chunks,
            document_type=document.document_type,
            category=document.category or 'normativa',
            tenant_id=document.tenant_id,
            industry_sectors=document.industry_sectors or [],
            authority=document.authority or 'Governo Italiano'
        )
        
        print(f'   Successfully added {len(result)} chunks to Weaviate')
        
        # Update document summary with more content
        if len(content) > 500:
            document.content_summary = content[:5000]  # Store first 5000 chars as summary
            db.commit()
            print('\n5. Updated document summary in database')
        
        # Test search
        print('\n6. Testing search...')
        test_queries = ['sicurezza lavoro', 'DPI', 'rischio', 'saldatura', 'taglio metalli']
        
        for query in test_queries:
            results = await vector_service.hybrid_search(
                query=query,
                filters={'tenant_id': document.tenant_id},
                limit=3,
                threshold=0.1
            )
            print(f'   Query "{query}": {len(results)} results')
        
        return True
        
    except Exception as e:
        import traceback
        print(f'ERROR: {e}')
        traceback.print_exc()
        return False
    finally:
        db.close()

def extract_keywords(text):
    """Extract relevant HSE keywords from text"""
    keywords = []
    
    # Common HSE keywords to look for
    hse_keywords = [
        'sicurezza', 'lavoro', 'rischio', 'DPI', 'protezione', 
        'infortunio', 'prevenzione', 'emergenza', 'formazione',
        'sorveglianza', 'salute', 'pericolo', 'incidente',
        'dispositivi', 'procedure', 'valutazione', 'D.Lgs', '81/08'
    ]
    
    text_lower = text.lower()
    for kw in hse_keywords:
        if kw.lower() in text_lower:
            keywords.append(kw)
    
    # Add specific article/section if found
    import re
    articles = re.findall(r'Art\.\s*(\d+)', text)
    if articles:
        keywords.extend([f'Art.{a}' for a in articles[:3]])
    
    return keywords[:10]  # Limit to 10 keywords

if __name__ == '__main__':
    document_id = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    print(f'Reprocessing document ID {document_id}')
    success = asyncio.run(reprocess_document(document_id))
    print(f'\n=== Reprocessing {"SUCCESSFUL" if success else "FAILED"} ===')
    sys.exit(0 if success else 1)