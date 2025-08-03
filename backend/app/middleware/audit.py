from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import json
import logging
from datetime import datetime

from app.config.database import SessionLocal
from app.core.audit import get_client_ip, get_user_agent


logger = logging.getLogger(__name__)


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware for comprehensive audit logging of all API requests
    """
    
    def __init__(self, app):
        super().__init__(app)
        
        # Configure which endpoints to audit
        self.audit_config = {
            "always_audit": [
                "/api/v1/auth/login",
                "/api/v1/auth/logout", 
                "/api/v1/permits/",
                "/api/v1/documents/"
            ],
            "never_audit": [
                "/health",
                "/",
                "/api/docs",
                "/api/redoc"
            ],
            "audit_methods": ["POST", "PUT", "DELETE", "PATCH"],
            "sensitive_headers": ["authorization", "cookie", "x-api-key"],
            "sensitive_fields": ["password", "token", "secret", "key"]
        }
    
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        
        # Check if this request should be audited
        should_audit = self._should_audit_request(request)
        
        if not should_audit:
            return await call_next(request)
        
        # Prepare audit data
        audit_data = await self._prepare_audit_data(request, start_time)
        
        try:
            # Process request
            response = await call_next(request)
            
            # Complete audit data with response info
            audit_data.update(await self._prepare_response_audit_data(response, start_time))
            
            # Log audit record
            await self._log_audit_record(audit_data)
            
            return response
            
        except Exception as e:
            # Log failed request
            audit_data.update({
                "response_status": 500,
                "error": str(e),
                "processing_time": time.time() - start_time,
                "success": False
            })
            
            await self._log_audit_record(audit_data)
            raise
    
    def _should_audit_request(self, request: Request) -> bool:
        """
        Determine if request should be audited
        """
        path = request.url.path
        method = request.method
        
        # Never audit certain endpoints
        for never_audit_path in self.audit_config["never_audit"]:
            if path.startswith(never_audit_path):
                return False
        
        # Always audit certain endpoints
        for always_audit_path in self.audit_config["always_audit"]:
            if path.startswith(always_audit_path):
                return True
        
        # Audit specific HTTP methods
        if method in self.audit_config["audit_methods"]:
            return True
        
        # Audit authenticated requests (has Authorization header)
        if request.headers.get("Authorization"):
            return True
        
        return False
    
    async def _prepare_audit_data(self, request: Request, start_time: float) -> dict:
        """
        Prepare audit data from request
        """
        # Extract basic request info
        audit_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "ip_address": get_client_ip(request),
            "user_agent": get_user_agent(request),
            "headers": self._sanitize_headers(dict(request.headers)),
            "start_time": start_time
        }
        
        # Extract tenant and user info if available
        tenant_id = getattr(request.state, "tenant_id", None)
        if tenant_id:
            audit_data["tenant_id"] = tenant_id
        
        # Try to extract user info from JWT
        user_info = await self._extract_user_info(request)
        if user_info:
            audit_data.update(user_info)
        
        # Extract request body for certain endpoints (be careful with sensitive data)
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await self._extract_request_body(request)
                if body:
                    audit_data["request_body"] = self._sanitize_body(body)
            except Exception as e:
                logger.warning(f"Failed to extract request body for audit: {e}")
        
        return audit_data
    
    async def _prepare_response_audit_data(self, response: Response, start_time: float) -> dict:
        """
        Prepare audit data from response
        """
        processing_time = time.time() - start_time
        
        return {
            "response_status": response.status_code,
            "processing_time": round(processing_time, 4),
            "success": 200 <= response.status_code < 400,
            "response_headers": self._sanitize_headers(dict(response.headers))
        }
    
    async def _extract_user_info(self, request: Request) -> dict:
        """
        Extract user information from JWT token
        """
        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return {}
            
            token = auth_header.replace("Bearer ", "")
            
            from app.core.security import decode_token
            payload = decode_token(token)
            
            return {
                "user_id": payload.get("sub"),
                "tenant_id": payload.get("tenant_id")
            }
            
        except Exception:
            return {}
    
    async def _extract_request_body(self, request: Request) -> dict:
        """
        Extract and parse request body
        """
        try:
            content_type = request.headers.get("content-type", "")
            
            if "application/json" in content_type:
                # For JSON requests, we need to read the body carefully
                # This is tricky because FastAPI will also try to read it
                body = await request.body()
                if body:
                    return json.loads(body.decode())
            
            # For other content types, just log that there was a body
            elif request.headers.get("content-length"):
                return {"_note": f"Request body present ({content_type})"}
            
            return {}
            
        except Exception as e:
            logger.warning(f"Error extracting request body: {e}")
            return {"_error": "Failed to extract body"}
    
    def _sanitize_headers(self, headers: dict) -> dict:
        """
        Remove sensitive information from headers
        """
        sanitized = {}
        
        for key, value in headers.items():
            key_lower = key.lower()
            
            if key_lower in self.audit_config["sensitive_headers"]:
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = value
        
        return sanitized
    
    def _sanitize_body(self, body: dict) -> dict:
        """
        Remove sensitive information from request body
        """
        if not isinstance(body, dict):
            return body
        
        sanitized = {}
        
        for key, value in body.items():
            key_lower = key.lower()
            
            # Check if field contains sensitive data
            if any(sensitive in key_lower for sensitive in self.audit_config["sensitive_fields"]):
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_body(value)
            else:
                sanitized[key] = value
        
        return sanitized
    
    async def _log_audit_record(self, audit_data: dict):
        """
        Log audit record to database
        """
        try:
            db = SessionLocal()
            
            try:
                from app.models.audit import AuditLog
                
                # Determine severity based on response
                severity = "info"
                if not audit_data.get("success", True):
                    severity = "error" if audit_data.get("response_status", 500) >= 500 else "warning"
                
                # Determine category
                category = self._determine_category(audit_data["path"], audit_data["method"])
                
                # Create audit log entry
                audit_log = AuditLog(
                    tenant_id=audit_data.get("tenant_id"),
                    user_id=audit_data.get("user_id"),
                    username=audit_data.get("username"),
                    action=f"{audit_data['method'].lower()}.{category}",
                    resource_type="api_request",
                    resource_name=audit_data["path"],
                    extra_data={
                        "query_params": audit_data.get("query_params", {}),
                        "processing_time": audit_data.get("processing_time"),
                        "response_status": audit_data.get("response_status"),
                        "request_body": audit_data.get("request_body", {}),
                        "headers": audit_data.get("headers", {})
                    },
                    ip_address=audit_data.get("ip_address"),
                    user_agent=audit_data.get("user_agent"),
                    api_endpoint=audit_data["path"],
                    severity=severity,
                    category=category
                )
                
                db.add(audit_log)
                db.commit()
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Failed to log audit record: {e}")
            # Don't fail the request if audit logging fails
    
    def _determine_category(self, path: str, method: str) -> str:
        """
        Determine audit category based on endpoint
        """
        if "/auth/" in path:
            return "authentication"
        elif "/permits/" in path:
            return "permit_management"
        elif "/documents/" in path:
            return "document_management"
        elif "/users/" in path:
            return "user_management"
        else:
            return "api_access"