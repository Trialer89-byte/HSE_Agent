from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging

from app.core.tenant import tenant_context


logger = logging.getLogger(__name__)


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware to manage tenant context throughout the request lifecycle
    """
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip tenant context for public endpoints
        public_endpoints = ["/", "/health", "/api/docs", "/api/redoc", "/api/v1/system/info"]
        
        if request.url.path in public_endpoints:
            response = await call_next(request)
            return response
        
        try:
            # Extract tenant information from request
            tenant_id = await self._extract_tenant_id(request)
            
            if tenant_id:
                # Set tenant context
                tenant_context.set_tenant(tenant_id)
                
                # Add tenant ID to request state for other middleware/handlers
                request.state.tenant_id = tenant_id
            
            # Process request
            response = await call_next(request)
            
            return response
            
        except Exception as e:
            logger.error(f"Tenant middleware error: {str(e)}")
            response = await call_next(request)
            return response
        
        finally:
            # Always clear tenant context after request
            tenant_context.clear()
    
    async def _extract_tenant_id(self, request: Request) -> int:
        """
        Extract tenant ID from various sources
        """
        # Method 1: From JWT token (most common)
        tenant_id = await self._extract_from_jwt(request)
        if tenant_id:
            return tenant_id
        
        # Method 2: From subdomain (if using subdomain routing)
        tenant_id = self._extract_from_subdomain(request)
        if tenant_id:
            return tenant_id
        
        # Method 3: From custom header
        tenant_id = self._extract_from_header(request)
        if tenant_id:
            return tenant_id
        
        return None
    
    async def _extract_from_jwt(self, request: Request) -> int:
        """
        Extract tenant ID from JWT token
        """
        try:
            # Get Authorization header
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return None
            
            token = auth_header.replace("Bearer ", "")
            
            # Decode token to get tenant_id
            from app.core.security import decode_token
            payload = decode_token(token)
            
            return payload.get("tenant_id")
            
        except Exception:
            # Token validation will be handled by auth middleware
            return None
    
    def _extract_from_subdomain(self, request: Request) -> int:
        """
        Extract tenant ID from subdomain (e.g., company.hse-system.com)
        """
        try:
            host = request.headers.get("Host", "")
            
            # Skip if localhost or IP address
            if "localhost" in host or host.replace(".", "").replace(":", "").isdigit():
                return None
            
            # Extract subdomain
            parts = host.split(".")
            if len(parts) >= 3:  # subdomain.domain.tld
                subdomain = parts[0]
                
                # Look up tenant by domain
                from app.config.database import SessionLocal
                from app.models.tenant import Tenant
                
                db = SessionLocal()
                try:
                    tenant = db.query(Tenant).filter(
                        Tenant.domain == host,
                        Tenant.is_active == True
                    ).first()
                    
                    return tenant.id if tenant else None
                    
                finally:
                    db.close()
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting tenant from subdomain: {e}")
            return None
    
    def _extract_from_header(self, request: Request) -> int:
        """
        Extract tenant ID from custom header (X-Tenant-ID)
        """
        try:
            tenant_header = request.headers.get("X-Tenant-ID")
            if tenant_header and tenant_header.isdigit():
                return int(tenant_header)
            return None
        except (ValueError, TypeError):
            return None