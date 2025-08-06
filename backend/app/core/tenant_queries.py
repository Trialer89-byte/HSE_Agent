from typing import TypeVar, Type, Optional, Any
from sqlalchemy.orm import Query, Session
from sqlalchemy import and_
from contextlib import contextmanager
import logging

from app.core.tenant import tenant_context
from app.models.base import TenantMixin
from app.models.tenant import Tenant
from app.services.tenant_database_service import tenant_db_service

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=TenantMixin)


class TenantAwareQuery:
    """
    Helper class to automatically apply tenant filters to database queries
    """
    
    @staticmethod
    def filter_by_tenant(query: Query, model_class: Type[ModelType]) -> Query:
        """
        Automatically apply tenant filter to query if model has tenant_id
        """
        current_tenant_id = tenant_context.current_tenant_id
        
        if current_tenant_id is None:
            logger.warning(f"No tenant context set for query on {model_class.__name__}")
            # For security, return empty query rather than all data
            return query.filter(False)
        
        # Check if model has tenant_id attribute
        if hasattr(model_class, 'tenant_id'):
            return query.filter(model_class.tenant_id == current_tenant_id)
        
        return query
    
    @staticmethod
    def create_tenant_aware_session(tenant: Optional[Tenant] = None) -> Session:
        """
        Create a database session with automatic tenant filtering
        """
        if tenant is None:
            tenant = tenant_context.current_tenant
        
        if tenant is None:
            raise ValueError("No tenant context available for database session")
        
        # Get appropriate session for tenant's deployment mode
        session_factory = tenant_db_service.get_tenant_session(tenant)
        return session_factory()


class TenantQueryManager:
    """
    Manager class for tenant-aware database operations
    """
    
    def __init__(self, db: Session, tenant: Optional[Tenant] = None):
        self.db = db
        self.tenant = tenant or tenant_context.current_tenant
        
        if self.tenant is None:
            raise ValueError("Tenant context required for TenantQueryManager")
    
    def query(self, model_class: Type[ModelType]) -> Query:
        """
        Create a tenant-filtered query
        """
        query = self.db.query(model_class)
        return TenantAwareQuery.filter_by_tenant(query, model_class)
    
    def get(self, model_class: Type[ModelType], id: Any) -> Optional[ModelType]:
        """
        Get a single record by ID with tenant filtering
        """
        return self.query(model_class).filter(model_class.id == id).first()
    
    def create(self, model_class: Type[ModelType], **kwargs) -> ModelType:
        """
        Create a new record with automatic tenant assignment
        """
        # Automatically set tenant_id if model supports it
        if hasattr(model_class, 'tenant_id') and 'tenant_id' not in kwargs:
            kwargs['tenant_id'] = self.tenant.id
        
        instance = model_class(**kwargs)
        self.db.add(instance)
        return instance
    
    def update(self, instance: ModelType, **kwargs) -> ModelType:
        """
        Update a record with tenant validation
        """
        # Validate that the instance belongs to current tenant
        if hasattr(instance, 'tenant_id') and instance.tenant_id != self.tenant.id:
            raise ValueError("Cannot update record from different tenant")
        
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        
        return instance
    
    def delete(self, instance: ModelType) -> bool:
        """
        Delete a record with tenant validation
        """
        # Validate that the instance belongs to current tenant
        if hasattr(instance, 'tenant_id') and instance.tenant_id != self.tenant.id:
            raise ValueError("Cannot delete record from different tenant")
        
        self.db.delete(instance)
        return True
    
    def bulk_delete(self, model_class: Type[ModelType], **filters) -> int:
        """
        Bulk delete with tenant filtering
        """
        query = self.query(model_class)
        
        # Apply additional filters
        for key, value in filters.items():
            if hasattr(model_class, key):
                query = query.filter(getattr(model_class, key) == value)
        
        deleted_count = query.count()
        query.delete(synchronize_session=False)
        
        return deleted_count
    
    def count(self, model_class: Type[ModelType], **filters) -> int:
        """
        Count records with tenant filtering
        """
        query = self.query(model_class)
        
        # Apply additional filters
        for key, value in filters.items():
            if hasattr(model_class, key):
                query = query.filter(getattr(model_class, key) == value)
        
        return query.count()


@contextmanager
def tenant_db_session(tenant: Optional[Tenant] = None):
    """
    Context manager for tenant-aware database sessions
    """
    if tenant is None:
        tenant = tenant_context.current_tenant
    
    if tenant is None:
        raise ValueError("Tenant context required for database session")
    
    with tenant_db_service.get_db_session(tenant) as db:
        manager = TenantQueryManager(db, tenant)
        try:
            yield manager
            db.commit()
        except Exception:
            db.rollback()
            raise


def get_tenant_query_manager(db: Session) -> TenantQueryManager:
    """
    Get a tenant query manager for the current database session
    """
    return TenantQueryManager(db)


# Decorator for automatic tenant filtering
def tenant_required(func):
    """
    Decorator to ensure tenant context is available for database operations
    """
    from functools import wraps
    import asyncio
    
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if tenant_context.current_tenant_id is None:
            raise ValueError("Tenant context required for this operation")
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            return func(*args, **kwargs)
    return wrapper