from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, JSONResponse
import logging
from typing import Optional

from app.core.tenant import tenant_context, get_tenant_from_domain
from app.config.database import SessionLocal
from app.models.tenant import Tenant


logger = logging.getLogger(__name__)


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Enhanced middleware to manage tenant context throughout the request lifecycle
    """
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip tenant context for public endpoints
        public_endpoints = [
            "/", "/health", "/api/docs", "/api/redoc", "/api/openapi.json",
            "/api/v1/system/info", "/api/v1/auth/login", "/api/v1/auth/register"
        ]
        
        # Skip tenant context for public tenant endpoints
        public_patterns = [
            "/api/v1/public/",
            "/api/v1/admin/"  # Admin endpoints handle their own tenant validation
        ]
        
        if request.url.path in public_endpoints:
            response = await call_next(request)
            return response
        
        # Check if path matches public patterns
        for pattern in public_patterns:
            if request.url.path.startswith(pattern):
                response = await call_next(request)
                return response
        
        try:
            # Extract tenant information from request
            tenant = await self._extract_tenant(request)
            
            if tenant:
                # Validate tenant is active
                if not tenant.is_active:
                    return JSONResponse(
                        status_code=status.HTTP_403_FORBIDDEN,
                        content={"error": "Tenant is inactive"}
                    )
                
                # Set tenant context
                tenant_context.set_tenant(tenant.id, tenant)
                
                # Add tenant info to request state
                request.state.tenant_id = tenant.id
                request.state.tenant = tenant
            else:
                # For paths that require tenant context, return error
                if request.url.path.startswith("/api/v1/") and not request.url.path.startswith("/api/v1/admin/"):
                    return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={"error": "Tenant identification required"}
                    )
            
            # Process request
            response = await call_next(request)
            
            return response
            
        except Exception as e:
            logger.error(f"Tenant middleware error: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "Tenant middleware error"}
            )
        
        finally:
            # Always clear tenant context after request
            tenant_context.clear()
    
    async def _extract_tenant(self, request: Request) -> Optional[Tenant]:
        """
        Extract tenant from various sources and return full tenant object
        """
        db = SessionLocal()
        try:
            # Method 1: From JWT token (most common)
            tenant = await self._extract_from_jwt(request, db)
            if tenant:
                return tenant
            
            # Method 2: From subdomain (if using subdomain routing)
            tenant = self._extract_from_subdomain(request, db)
            if tenant:
                return tenant
            
            # Method 3: From custom header
            tenant = self._extract_from_header(request, db)
            if tenant:
                return tenant
            
            return None
        finally:
            db.close()
    
    async def _extract_from_jwt(self, request: Request, db) -> Optional[Tenant]:
        """
        Extract tenant from JWT token
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
            tenant_id = payload.get("tenant_id")
            
            if tenant_id:
                return db.query(Tenant).filter_by(id=tenant_id, is_active=True).first()
            
            return None
            
        except Exception:
            # Token validation will be handled by auth middleware
            return None
    
    def _extract_from_subdomain(self, request: Request, db) -> Optional[Tenant]:
        """
        Extract tenant from subdomain (e.g., company.hse-system.com)
        """
        try:
            host = request.headers.get("Host", "")
            
            # Skip if localhost or IP address
            if "localhost" in host or host.replace(".", "").replace(":", "").isdigit():
                return None
            
            # Look up tenant by exact domain match first
            tenant = db.query(Tenant).filter(
                Tenant.domain == host,
                Tenant.is_active == True
            ).first()
            
            if tenant:
                return tenant
            
            # Extract subdomain and try partial match
            parts = host.split(".")
            if len(parts) >= 3:  # subdomain.domain.tld
                subdomain = parts[0]
                base_domain = ".".join(parts[1:])
                
                # Look for tenant with matching subdomain pattern
                tenant = db.query(Tenant).filter(
                    Tenant.domain.like(f"{subdomain}.%"),
                    Tenant.is_active == True
                ).first()
                
                return tenant
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting tenant from subdomain: {e}")
            return None
    
    def _extract_from_header(self, request: Request, db) -> Optional[Tenant]:
        """
        Extract tenant from custom header (X-Tenant-ID or X-Tenant-Domain)
        """
        try:
            # Try tenant ID header first
            tenant_id_header = request.headers.get("X-Tenant-ID")
            if tenant_id_header and tenant_id_header.isdigit():
                tenant_id = int(tenant_id_header)
                return db.query(Tenant).filter_by(id=tenant_id, is_active=True).first()
            
            # Try tenant domain header
            tenant_domain_header = request.headers.get("X-Tenant-Domain")
            if tenant_domain_header:
                return db.query(Tenant).filter_by(domain=tenant_domain_header, is_active=True).first()
            
            return None
        except (ValueError, TypeError):
            return None