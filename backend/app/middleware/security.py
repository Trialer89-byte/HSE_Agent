from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import redis
from typing import Dict, Any
import logging

from app.config.settings import settings


logger = logging.getLogger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Security middleware for rate limiting, IP filtering, and security headers
    """
    
    def __init__(self, app):
        super().__init__(app)
        
        # Initialize Redis for rate limiting
        try:
            self.redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
            self.redis_client.ping()
            self.rate_limiting_enabled = True
        except Exception as e:
            logger.warning(f"Redis not available for rate limiting: {e}")
            self.rate_limiting_enabled = False
        
        # Rate limiting configuration
        self.rate_limits = {
            "default": {"requests": settings.rate_limit_per_minute, "window": 60},
            "login": {"requests": 5, "window": 300},  # 5 attempts per 5 minutes
            "analysis": {"requests": 10, "window": 60}  # 10 analysis per minute
        }
    
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        
        # Skip middleware for health checks, docs, and OPTIONS requests
        if request.url.path in ["/health", "/", "/api/docs", "/api/redoc"] or request.method == "OPTIONS":
            response = await call_next(request)
            return self._add_security_headers(response)
        
        try:
            # 1. Rate limiting
            if self.rate_limiting_enabled:
                await self._check_rate_limits(request)
            
            # 2. Security validations
            await self._validate_request_security(request)
            
            # 3. Process request
            response = await call_next(request)
            
            # 4. Add security headers
            response = self._add_security_headers(response)
            
            # 5. Log timing
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={"error": e.detail}
            )
        except Exception as e:
            logger.error(f"Security middleware error: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"error": "Internal security error"}
            )
    
    async def _check_rate_limits(self, request: Request):
        """
        Check rate limits based on IP and endpoint
        """
        client_ip = self._get_client_ip(request)
        endpoint_type = self._get_endpoint_type(request.url.path)
        
        # Get rate limit configuration
        rate_config = self.rate_limits.get(endpoint_type, self.rate_limits["default"])
        
        # Create Redis key
        redis_key = f"rate_limit:{client_ip}:{endpoint_type}"
        
        try:
            # Get current request count
            current_requests = self.redis_client.get(redis_key)
            
            if current_requests is None:
                # First request in window
                self.redis_client.setex(redis_key, rate_config["window"], 1)
            else:
                current_requests = int(current_requests)
                
                if current_requests >= rate_config["requests"]:
                    # Rate limit exceeded
                    logger.warning(f"Rate limit exceeded for IP {client_ip} on endpoint {endpoint_type}")
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Rate limit exceeded. Try again later."
                    )
                
                # Increment counter
                self.redis_client.incr(redis_key)
                
        except redis.RedisError as e:
            logger.error(f"Redis error in rate limiting: {e}")
            # Continue without rate limiting if Redis fails
    
    async def _validate_request_security(self, request: Request):
        """
        Validate request for security issues
        """
        # Check for suspiciously large headers
        total_header_size = sum(len(k) + len(v) for k, v in request.headers.items())
        if total_header_size > 8192:  # 8KB limit
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request headers too large"
            )
        
        # Check for malicious patterns in URL
        suspicious_patterns = ["../", "\\", "<script", "javascript:", "data:", "vbscript:"]
        url_path = request.url.path.lower()
        
        for pattern in suspicious_patterns:
            if pattern in url_path:
                logger.warning(f"Suspicious pattern '{pattern}' detected in URL: {request.url.path}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid request"
                )
        
        # Validate Content-Type for POST/PUT requests
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            allowed_types = [
                "application/json",
                "application/x-www-form-urlencoded",
                "multipart/form-data"
            ]
            
            if not any(allowed_type in content_type for allowed_type in allowed_types):
                logger.warning(f"Invalid Content-Type: {content_type}")
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail="Unsupported media type"
                )
    
    def _add_security_headers(self, response: Response) -> Response:
        """
        Add security headers to response
        """
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            "Cache-Control": "no-store, no-cache, must-revalidate, proxy-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
        
        # Add HSTS in production with HTTPS
        if settings.environment == "production":
            security_headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Add CSP for HTML responses (disabled in development)
        content_type = response.headers.get("content-type", "")
        if "text/html" in content_type and settings.environment == "production":
            security_headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "connect-src 'self'"
            )
        # CSP disabled in development to allow API docs to work properly
        
        # Apply headers
        for header, value in security_headers.items():
            response.headers[header] = value
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP address considering proxies
        """
        # Check for forwarded headers first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct connection
        return str(request.client.host) if request.client else "unknown"
    
    def _get_endpoint_type(self, path: str) -> str:
        """
        Determine endpoint type for rate limiting
        """
        if "/auth/login" in path:
            return "login"
        elif "/analyze" in path:
            return "analysis"
        else:
            return "default"