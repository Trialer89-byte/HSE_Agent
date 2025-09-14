import sys
import os
import asyncio
sys.path.append('/app')

from app.database import get_db
from app.models.document import Document
from app.services.vector_service import VectorService


async def main():
    """Check and fix Weaviate sync for HSE-4064 document"""
    db = next(get_db())
    vector_service = VectorService()
    
    # Get HSE-4064 document
    document = db.query(Document).filter(Document.id == 10).first()
    if not document:
        print("Document not found")
        return
    
    print(f"Found document: {document.title}")
    
    # Test search in Weaviate
    results = await vector_service.hybrid_search(
        query="working height HSE-4064",
        filters={"tenant_id": document.tenant_id},
        limit=5
    )
    
    print(f"Found {len(results)} results in Weaviate")
    for i, result in enumerate(results):
        print(f"  {i+1}. {result.get('title', 'No title')} - {result.get('document_code', 'No code')}")
    
    db.close()

if __name__ == "__main__":
    asyncio.run(main())