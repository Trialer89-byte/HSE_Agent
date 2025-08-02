from typing import Optional
from fastapi import HTTPException, status, Request
from sqlalchemy.orm import Session

from app.models.tenant import Tenant
from app.models.user import User


class TenantContext:
    """
    Manages tenant context for multi-tenant operations
    """
    
    def __init__(self):
        self.current_tenant_id: Optional[int] = None
        self.current_tenant: Optional[Tenant] = None
    
    def set_tenant(self, tenant_id: int, tenant: Tenant = None):
        """Set current tenant context"""
        self.current_tenant_id = tenant_id
        self.current_tenant = tenant
    
    def clear(self):
        """Clear tenant context"""
        self.current_tenant_id = None
        self.current_tenant = None


# Global tenant context
tenant_context = TenantContext()


def get_tenant_from_domain(domain: str, db: Session) -> Optional[Tenant]:
    """
    Get tenant by domain name
    """
    return db.query(Tenant).filter(
        Tenant.domain == domain,
        Tenant.is_active == True
    ).first()


def get_tenant_from_user(user: User, db: Session) -> Optional[Tenant]:
    """
    Get tenant from user
    """
    return db.query(Tenant).filter(
        Tenant.id == user.tenant_id,
        Tenant.is_active == True
    ).first()


def enforce_tenant_isolation(user: User, resource_tenant_id: int):
    """
    Enforce tenant isolation for resource access
    """
    # Super admin can access all tenants
    if user.role == "super_admin":
        return
    
    # Regular users can only access their tenant's resources
    if user.tenant_id != resource_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: resource belongs to different tenant"
        )


def validate_tenant_limits(tenant: Tenant, operation: str, db: Session) -> bool:
    """
    Validate tenant limits for operations
    """
    if operation == "create_user":
        user_count = db.query(User).filter_by(tenant_id=tenant.id).count()
        return user_count < tenant.max_users
    
    elif operation == "upload_document":
        from app.models.document import Document
        doc_count = db.query(Document).filter_by(tenant_id=tenant.id).count()
        return doc_count < tenant.max_documents
    
    return True


def get_tenant_settings(tenant: Tenant) -> dict:
    """
    Get tenant-specific settings
    """
    default_settings = {
        "max_file_size_mb": 50,
        "allowed_file_types": [".pdf", ".docx", ".doc", ".txt"],
        "ai_analysis_enabled": True,
        "audit_retention_days": 365,
        "require_approval": True,
        "custom_fields": {}
    }
    
    # Merge with tenant-specific settings
    if tenant.settings:
        default_settings.update(tenant.settings)
    
    return default_settings