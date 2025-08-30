"""
Test Document Router - FOR TESTING ONLY
Allows document upload without authentication
"""
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.services.document_service import DocumentService
from app.schemas.document import DocumentResponse

router = APIRouter(
    prefix="/api/v1/test/documents",
    tags=["test-documents"]
)


@router.post("/upload")
async def upload_document_test(
    file: UploadFile = File(...),
    document_code: Optional[str] = Form(None),
    title: str = Form(...),
    document_type: str = Form(...),
    category: Optional[str] = Form(None),
    subcategory: Optional[str] = Form(None),
    authority: Optional[str] = Form(None),
    scope: Optional[str] = Form(None),
    industry_sectors: Optional[str] = Form(None),
    tenant_id: int = Form(1),  # Default tenant for testing
    db: Session = Depends(get_db)
):
    """
    TEST ENDPOINT - Upload document without authentication
    
    - **file**: The document file (PDF, DOCX, DOC, TXT)
    - **document_code**: Optional unique code
    - **title**: Document title
    - **document_type**: Type (normativa, istruzione_operativa, procedura_sicurezza)
    - **category**: Optional category
    - **tenant_id**: Tenant ID (default: 1)
    """
    
    # Parse industry sectors
    sectors = []
    if industry_sectors:
        sectors = [s.strip() for s in industry_sectors.split(",") if s.strip()]
    
    # Create document service
    document_service = DocumentService(db)
    
    try:
        # Upload document with fixed tenant and user
        document = await document_service.upload_document(
            file=file,
            document_code=document_code,
            title=title,
            document_type=document_type,
            category=category,
            tenant_id=tenant_id,
            uploaded_by=1,  # Default admin user
            industry_sectors=sectors,
            authority=authority,
            subcategory=subcategory,
            scope=scope
        )
        
        return DocumentResponse(
            id=document.id,
            document_code=document.document_code,
            title=document.title,
            document_type=document.document_type,
            category=document.category,
            subcategory=document.subcategory,
            scope=document.scope,
            industry_sectors=document.industry_sectors,
            authority=document.authority,
            file_path=document.file_path,
            version=document.version,
            is_active=document.is_active,
            visibility=document.visibility,
            uploaded_by=document.uploaded_by,
            created_at=document.created_at,
            updated_at=document.updated_at,
            tenant_id=document.tenant_id,
            keywords=document.keywords or [],
            content_summary=document.content_summary
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error uploading document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {str(e)}"
        )


@router.get("/list")
async def list_documents_test(
    tenant_id: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    TEST ENDPOINT - List documents without authentication
    """
    from app.models.document import Document
    
    documents = db.query(Document).filter(
        Document.tenant_id == tenant_id,
        Document.is_active == True
    ).limit(limit).all()
    
    return {
        "total": len(documents),
        "documents": [
            {
                "id": doc.id,
                "title": doc.title,
                "document_code": doc.document_code,
                "document_type": doc.document_type,
                "category": doc.category,
                "created_at": doc.created_at
            }
            for doc in documents
        ]
    }


@router.delete("/{document_id}")
async def delete_document_test(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    TEST ENDPOINT - Delete document without authentication
    """
    from app.models.document import Document
    
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Soft delete
    document.is_active = False
    db.commit()
    
    return {"message": f"Document {document_id} deleted"}