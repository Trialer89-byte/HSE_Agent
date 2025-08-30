from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel, Field


class DocumentBase(BaseModel):
    document_code: Optional[str] = None
    title: str
    document_type: str
    category: Optional[str] = None
    subcategory: Optional[str] = None
    scope: Optional[str] = None
    industry_sectors: Optional[List[str]] = Field(default_factory=list)
    authority: Optional[str] = None


class DocumentResponse(DocumentBase):
    id: int
    tenant_id: int
    file_path: Optional[str] = None
    file_hash: Optional[str] = None
    content_summary: Optional[str] = None
    vector_id: Optional[str] = None
    version: str
    publication_date: Optional[date] = None
    effective_date: Optional[date] = None
    is_active: bool
    uploaded_by: int
    created_at: datetime
    updated_at: datetime
    
    # AI fields
    keywords: List[str] = Field(default_factory=list)
    relevance_score: float = 0.0
    
    class Config:
        from_attributes = True


class DocumentUpdateRequest(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    industry_sectors: Optional[List[str]] = None
    authority: Optional[str] = None
    scope: Optional[str] = None


class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int
    limit: int
    offset: int


class DocumentVersionResponse(BaseModel):
    id: int
    document_code: str
    title: str
    version: str
    file_hash: Optional[str] = None
    publication_date: Optional[date] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class DocumentSearchRequest(BaseModel):
    query: str
    document_types: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    industry_sectors: Optional[List[str]] = None
    limit: int = Field(default=20, ge=1, le=100)
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)


class DocumentSearchResult(BaseModel):
    document_id: int
    document_code: str
    title: str
    document_type: str
    category: str
    chunk_content: str
    search_score: float
    
    class Config:
        from_attributes = True