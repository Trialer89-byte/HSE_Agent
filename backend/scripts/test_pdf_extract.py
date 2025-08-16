#!/usr/bin/env python
import sys
sys.path.insert(0, '/app')

from app.services.storage_service import StorageService
import pypdf
import io

# Get the PDF from MinIO
storage = StorageService()

try:
    # Download the PDF
    response = storage.client.get_object('hse-documents', 'documents/1/dl81_2008_20250813150816_1.0.pdf')
    pdf_data = response.read()
    response.close()
    response.release_conn()
    
    print(f'Downloaded PDF: {len(pdf_data)} bytes')
    
    # Extract text using pypdf
    pdf_file = io.BytesIO(pdf_data)
    pdf_reader = pypdf.PdfReader(pdf_file)
    
    print(f'PDF has {len(pdf_reader.pages)} pages')
    
    # Extract text from first few pages
    content = ""
    for i, page in enumerate(pdf_reader.pages[:5]):  # First 5 pages
        page_text = page.extract_text()
        content += page_text + "\n"
        print(f'\nPage {i+1} extracted: {len(page_text)} characters')
        print(f'First 200 chars: {page_text[:200]}...')
    
    print(f'\nTotal extracted from first 5 pages: {len(content)} characters')
    
    # Check if content contains important keywords
    keywords = ['sicurezza', 'lavoro', 'rischio', 'DPI', 'protezione']
    found_keywords = [kw for kw in keywords if kw.lower() in content.lower()]
    print(f'Found keywords: {found_keywords}')
    
except Exception as e:
    import traceback
    print(f'Error: {e}')
    traceback.print_exc()