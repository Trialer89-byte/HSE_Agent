from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
import asyncio
from datetime import datetime

from app.config.database import get_db
from app.services.auth_service import get_current_user
from app.models.user import User
from app.models.document import Document
from app.services.document_service import DocumentService
from app.schemas.document import (
    DocumentResponse,
    DocumentListResponse,
    DocumentUpdateRequest,
    DocumentVersionResponse
)


router = APIRouter(
    prefix="/api/v1/documents",
    tags=["documents"],
    dependencies=[Depends(get_current_user)]
)

# Global dictionary to track upload progress
upload_progress: Dict[str, Dict[str, Any]] = {}


async def process_document_upload(
    task_id: str,
    file_content: bytes,
    file_name: str,
    document_code: Optional[str],
    title: str,
    document_type: str,
    category: Optional[str],
    tenant_id: int,
    uploaded_by: int,
    industry_sectors: List[str],
    authority: Optional[str],
    subcategory: Optional[str],
    scope: Optional[str],
    force_reload: bool,
    db_session: Session
):
    """Background task to process document upload"""
    try:
        print(f"[DEBUG] Starting background task for {task_id}")
        # Update progress
        upload_progress[task_id]["status"] = "processing"
        upload_progress[task_id]["progress"] = 10
        upload_progress[task_id]["message"] = "Processing document..."
        
        # Create a file-like object
        import io
        from fastapi import UploadFile
        
        file_like = io.BytesIO(file_content)
        upload_file = UploadFile(filename=file_name, file=file_like)
        
        # Create document service with progress callback
        document_service = DocumentService(db_session)
        
        # Add progress callback to document service
        original_add_chunks = document_service.vector_service.add_document_chunks
        
        async def add_chunks_with_progress(*args, **kwargs):
            chunks = args[5] if len(args) > 5 else kwargs.get('chunks', [])
            total_chunks = len(chunks)
            
            # Update progress
            upload_progress[task_id]["status"] = "vectorizing"
            upload_progress[task_id]["message"] = f"Creating {total_chunks} vector embeddings..."
            
            # Call original method
            result = await original_add_chunks(*args, **kwargs)
            
            # Update completion
            upload_progress[task_id]["progress"] = 90
            upload_progress[task_id]["message"] = "Finalizing document..."
            
            return result
        
        document_service.vector_service.add_document_chunks = add_chunks_with_progress
        
        # Process document
        print(f"[DEBUG] Calling document_service.upload_document for {task_id}")
        document = await document_service.upload_document(
            file=upload_file,
            document_code=document_code,
            title=title,
            document_type=document_type,
            category=category,
            tenant_id=tenant_id,
            uploaded_by=uploaded_by,
            industry_sectors=industry_sectors,
            authority=authority,
            subcategory=subcategory,
            scope=scope,
            force_reload=force_reload
        )
        
        # Update success
        print(f"[DEBUG] Document upload completed successfully for {task_id}, document_id: {document.id}")
        upload_progress[task_id]["status"] = "completed"
        upload_progress[task_id]["progress"] = 100
        upload_progress[task_id]["message"] = "Document uploaded successfully"
        upload_progress[task_id]["document_id"] = document.id
        upload_progress[task_id]["completed_at"] = datetime.now()
        
    except Exception as e:
        print(f"[ERROR] Upload failed for {task_id}: {str(e)}")
        import traceback
        print(f"[ERROR] Full traceback: {traceback.format_exc()}")
        # Update error
        upload_progress[task_id]["status"] = "failed"
        upload_progress[task_id]["error"] = str(e)
        upload_progress[task_id]["message"] = f"Upload failed: {str(e)}"
        upload_progress[task_id]["completed_at"] = datetime.now()


@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    document_code: Optional[str] = Form(None),
    title: str = Form(...),
    document_type: str = Form(...),
    category: Optional[str] = Form(None),
    subcategory: Optional[str] = Form(None),
    authority: Optional[str] = Form(None),
    scope: Optional[str] = Form(None),
    industry_sectors: Optional[str] = Form(None),
    force_reload: bool = Form(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a new document or create a new version of an existing document.
    
    - **file**: The document file (PDF, DOCX, DOC, TXT)
    - **document_code**: Optional unique code for the document (auto-generated if not provided)
    - **title**: Document title
    - **document_type**: Type of document (normativa, istruzione_operativa, etc.)
    - **category**: Optional category (auto-extracted by AI if not provided)
    - **subcategory**: Optional subcategory (auto-extracted by AI if not provided)
    - **authority**: Optional issuing authority (auto-extracted by AI if not provided)
    - **scope**: Optional document scope (auto-extracted by AI if not provided)
    - **industry_sectors**: Optional comma-separated list of applicable sectors (auto-extracted by AI if not provided)
    - **force_reload**: Force re-analysis even if file hash exists
    """
    # Generate a unique task ID
    import uuid
    task_id = str(uuid.uuid4())
    
    # Initialize progress tracking
    upload_progress[task_id] = {
        "status": "starting",
        "progress": 0,
        "message": "Initializing upload...",
        "started_at": datetime.now(),
        "document_id": None,
        "error": None
    }
    
    # Parse industry sectors
    sectors = []
    if industry_sectors:
        sectors = [s.strip() for s in industry_sectors.split(",") if s.strip()]
    
    # Read file content before background task
    file_content = await file.read()
    file_name = file.filename
    await file.seek(0)
    
    # Add background task
    background_tasks.add_task(
        process_document_upload,
        task_id=task_id,
        file_content=file_content,
        file_name=file_name,
        document_code=document_code,
        title=title,
        document_type=document_type,
        category=category,
        tenant_id=current_user.tenant_id,
        uploaded_by=current_user.id,
        industry_sectors=sectors,
        authority=authority,
        subcategory=subcategory,
        scope=scope,
        force_reload=force_reload,
        db_session=db
    )
    
    # Return immediately with task ID
    return {
        "task_id": task_id,
        "status": "processing",
        "message": "Document upload started. Use /api/documents/upload/status/{task_id} to check progress."
    }


@router.get("/upload/status/{task_id}")
async def get_upload_status(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Check the status of a document upload task.
    """
    if task_id not in upload_progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    progress_data = upload_progress[task_id].copy()
    
    # Clean up old completed tasks (older than 1 hour)
    if progress_data.get("completed_at"):
        elapsed = datetime.now() - progress_data["completed_at"]
        if elapsed.total_seconds() > 3600:  # 1 hour
            del upload_progress[task_id]
    
    return progress_data


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    document_type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List documents for the current tenant with optional filtering.
    """
    document_service = DocumentService(db)
    
    documents = document_service.get_documents_by_tenant(
        tenant_id=current_user.tenant_id,
        document_type=document_type,
        category=category,
        limit=limit,
        offset=offset
    )
    
    # Get total count
    total_query = db.query(Document).filter(
        Document.tenant_id == current_user.tenant_id,
        Document.is_active == True
    )
    
    if document_type:
        total_query = total_query.filter(Document.document_type == document_type)
    if category:
        total_query = total_query.filter(Document.category == category)
    
    total = total_query.count()
    
    return DocumentListResponse(
        documents=[DocumentResponse.from_orm(doc) for doc in documents],
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific document by ID.
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.tenant_id == current_user.tenant_id,
        Document.is_active == True
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return DocumentResponse.from_orm(document)


@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document_metadata(
    document_id: int,
    update_data: DocumentUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update document metadata without re-uploading the file.
    """
    document_service = DocumentService(db)
    
    try:
        document = await document_service.update_document_metadata(
            document_id=document_id,
            tenant_id=current_user.tenant_id,
            title=update_data.title,
            category=update_data.category,
            subcategory=update_data.subcategory,
            industry_sectors=update_data.industry_sectors,
            authority=update_data.authority,
            scope=update_data.scope
        )
        
        return DocumentResponse.from_orm(document)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update document: {str(e)}"
        )


@router.get("/versions/{document_code}", response_model=List[DocumentVersionResponse])
async def get_document_versions(
    document_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all versions of a document by document code.
    """
    document_service = DocumentService(db)
    
    versions = document_service.get_document_versions(
        document_code=document_code,
        tenant_id=current_user.tenant_id
    )
    
    return [DocumentVersionResponse.from_orm(doc) for doc in versions]


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a document and its vector embeddings.
    """
    document_service = DocumentService(db)
    
    success = await document_service.delete_document(
        document_id=document_id,
        tenant_id=current_user.tenant_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or could not be deleted"
        )
    
    return {"message": "Document deleted successfully"}


@router.post("/{document_id}/reanalyze", response_model=DocumentResponse)
async def reanalyze_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Re-analyze an existing document to update its vector embeddings and AI analysis.
    """
    # Get the document
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.tenant_id == current_user.tenant_id,
        Document.is_active == True
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Create a temporary file-like object from the stored file
    from app.services.storage_service import StorageService
    storage_service = StorageService()
    
    try:
        # Download the file content
        file_content = await storage_service.get_file(document.file_path)
        
        # Create an UploadFile-like object
        import io
        from fastapi import UploadFile
        
        file_like = io.BytesIO(file_content)
        filename = document.file_path.split("/")[-1]
        
        upload_file = UploadFile(
            filename=filename,
            file=file_like
        )
        
        # Re-upload with force_reload
        document_service = DocumentService(db)
        
        reanalyzed_doc = await document_service.upload_document(
            file=upload_file,
            document_code=document.document_code,
            title=document.title,
            document_type=document.document_type,
            category=document.category,
            tenant_id=current_user.tenant_id,
            uploaded_by=current_user.id,
            industry_sectors=document.industry_sectors,
            authority=document.authority,
            subcategory=document.subcategory,
            scope=document.scope,
            force_reload=True
        )
        
        return DocumentResponse.from_orm(reanalyzed_doc)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to re-analyze document: {str(e)}"
        )