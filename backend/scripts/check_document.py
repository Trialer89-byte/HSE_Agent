#!/usr/bin/env python
import sys
sys.path.insert(0, '/app')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.document import Document
from app.config.settings import settings

# Create database connection
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

doc = db.query(Document).filter(Document.id == 2).first()

if doc:
    print(f'Document ID: {doc.id}')
    print(f'Title: {doc.title}')
    print(f'Document code: {doc.document_code}')
    print(f'File path: {doc.file_path}')
    print(f'File hash: {doc.file_hash[:16]}...' if doc.file_hash else 'No hash')
    print(f'Content summary: {doc.content_summary[:200]}...' if doc.content_summary else 'No summary')
    print(f'Created at: {doc.created_at}')
    print(f'Is active: {doc.is_active}')
    
    # Check MinIO
    from app.services.storage_service import StorageService
    storage = StorageService()
    
    try:
        if doc.file_path:
            stat = storage.client.stat_object('hse-documents', doc.file_path)
            print(f'\nFile in MinIO:')
            print(f'  Size: {stat.size} bytes')
            print(f'  Modified: {stat.last_modified}')
            
            # Try to read first 1000 bytes
            response = storage.client.get_object('hse-documents', doc.file_path)
            data = response.read(1000)
            response.close()
            response.release_conn()
            
            print(f'  First 100 chars: {data[:100]}')
            
    except Exception as e:
        print(f'MinIO error: {e}')
else:
    print('Document not found')

db.close()