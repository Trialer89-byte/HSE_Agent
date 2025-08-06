from typing import Optional, Dict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import logging

from app.models.tenant import Tenant, DeploymentMode
from app.config.database import SessionLocal
from app.config.settings import settings

logger = logging.getLogger(__name__)


class TenantDatabaseService:
    """
    Service to manage database connections for different tenant deployment modes
    """
    
    def __init__(self):
        self._tenant_engines: Dict[int, object] = {}
        self._tenant_sessions: Dict[int, sessionmaker] = {}
    
    def get_tenant_session(self, tenant: Tenant) -> sessionmaker:
        """
        Get appropriate database session for tenant based on deployment mode
        """
        if tenant.deployment_mode == DeploymentMode.SAAS:
            # Use shared SaaS database
            return SessionLocal
        
        elif tenant.deployment_mode == DeploymentMode.ON_PREMISE:
            # Use tenant-specific database
            return self._get_tenant_specific_session(tenant)
        
        elif tenant.deployment_mode == DeploymentMode.HYBRID:
            # Use tenant-specific database but managed by us
            return self._get_tenant_specific_session(tenant)
        
        else:
            # Default to SaaS mode
            logger.warning(f"Unknown deployment mode for tenant {tenant.id}, defaulting to SaaS")
            return SessionLocal
    
    def _get_tenant_specific_session(self, tenant: Tenant) -> sessionmaker:
        """
        Get or create tenant-specific database session
        """
        if tenant.id in self._tenant_sessions:
            return self._tenant_sessions[tenant.id]
        
        if not tenant.database_url:
            raise ValueError(f"Database URL not configured for tenant {tenant.id}")
        
        try:
            # Create tenant-specific engine
            engine = create_engine(
                tenant.database_url,
                pool_pre_ping=True,
                pool_recycle=300,
                echo=settings.debug
            )
            
            # Create session factory
            session_factory = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=engine
            )
            
            # Cache the session factory
            self._tenant_engines[tenant.id] = engine
            self._tenant_sessions[tenant.id] = session_factory
            
            logger.info(f"Created database connection for tenant {tenant.id}")
            return session_factory
            
        except Exception as e:
            logger.error(f"Failed to create database connection for tenant {tenant.id}: {e}")
            raise
    
    @contextmanager
    def get_db_session(self, tenant: Tenant):
        """
        Context manager for tenant database sessions
        """
        session_factory = self.get_tenant_session(tenant)
        db = session_factory()
        try:
            yield db
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
    
    def validate_tenant_database(self, tenant: Tenant) -> bool:
        """
        Validate that tenant database is accessible and properly configured
        """
        try:
            with self.get_db_session(tenant) as db:
                # Simple query to test connection
                db.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Tenant database validation failed for {tenant.id}: {e}")
            return False
    
    def initialize_tenant_database(self, tenant: Tenant) -> bool:
        """
        Initialize database schema for on-premise tenant
        """
        if tenant.deployment_mode == DeploymentMode.SAAS:
            # No initialization needed for SaaS
            return True
        
        try:
            from app.config.database import Base
            
            # Get tenant-specific engine
            session_factory = self._get_tenant_specific_session(tenant)
            engine = self._tenant_engines[tenant.id]
            
            # Create all tables
            Base.metadata.create_all(bind=engine)
            
            logger.info(f"Initialized database schema for tenant {tenant.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize database for tenant {tenant.id}: {e}")
            return False
    
    def cleanup_tenant_connection(self, tenant_id: int):
        """
        Clean up tenant-specific database connections
        """
        if tenant_id in self._tenant_engines:
            try:
                self._tenant_engines[tenant_id].dispose()
                del self._tenant_engines[tenant_id]
                del self._tenant_sessions[tenant_id]
                logger.info(f"Cleaned up database connection for tenant {tenant_id}")
            except Exception as e:
                logger.error(f"Error cleaning up tenant connection {tenant_id}: {e}")


# Global instance
tenant_db_service = TenantDatabaseService()