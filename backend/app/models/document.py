from sqlalchemy import Column, Integer, String, Text, JSON, Float, Date, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.config.database import Base
from .base import TimestampMixin, TenantMixin


class Document(Base, TimestampMixin, TenantMixin):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    
    document_code = Column(String(100), nullable=False)
    title = Column(String(500), nullable=False)
    document_type = Column(String(50), nullable=False, index=True)
    category = Column(String(100))
    subcategory = Column(String(100))
    
    # Scope & Applicability
    scope = Column(String(50), default="tenant")
    industry_sectors = Column(JSON, default=[])
    applicable_departments = Column(JSON, default=[])
    
    # Content & Storage
    file_path = Column(String(500))
    file_hash = Column(String(64), index=True)  # SHA256 hash of file content
    content_summary = Column(Text)
    vector_id = Column(String(100), index=True)
    
    # AI Processing
    relevance_score = Column(Float, default=0.0)
    
    # Versioning & Lifecycle
    version = Column(String(20), default="1.0")
    parent_document_id = Column(Integer, ForeignKey("documents.id"))
    authority = Column(String(200))
    publication_date = Column(Date)
    effective_date = Column(Date)
    is_active = Column(Boolean, default=True)
    
    # Access Control
    visibility = Column(String(50), default="tenant")
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    tenant = relationship("Tenant", back_populates="documents")
    uploader = relationship("User", back_populates="uploaded_documents")
    parent_document = relationship("Document", remote_side=[id])
    
    # Unique constraints
    __table_args__ = (
        UniqueConstraint('tenant_id', 'document_code', 'version', name='_tenant_document_version_uc'),
    )
    
    def __repr__(self):
        return f"<Document(id={self.id}, code='{self.document_code}', title='{self.title}')>"