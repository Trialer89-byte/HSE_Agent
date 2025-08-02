from sqlalchemy import Column, Integer, String, Boolean, JSON, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.config.database import Base
from .base import TimestampMixin, TenantMixin


class User(Base, TimestampMixin, TenantMixin):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    
    # RBAC
    role = Column(String(50), default="viewer")
    permissions = Column(JSON, default=[])
    department = Column(String(100))
    
    # Security
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    failed_login_attempts = Column(Integer, default=0)
    last_login = Column(DateTime)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    created_permits = relationship("WorkPermit", foreign_keys="WorkPermit.created_by", back_populates="creator")
    approved_permits = relationship("WorkPermit", foreign_keys="WorkPermit.approved_by", back_populates="approver")
    uploaded_documents = relationship("Document", back_populates="uploader")
    audit_logs = relationship("AuditLog", back_populates="user")
    
    # Unique constraints
    __table_args__ = (
        UniqueConstraint('tenant_id', 'username', name='_tenant_username_uc'),
        UniqueConstraint('tenant_id', 'email', name='_tenant_email_uc'),
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', tenant_id={self.tenant_id})>"
    
    @property
    def full_name(self):
        return f"{self.first_name or ''} {self.last_name or ''}".strip() or self.username
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        from app.core.permissions import has_permission
        return has_permission(self, permission)