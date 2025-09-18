from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import logging
from datetime import datetime

from app.config.settings import settings
from app.config.database import Base, engine
from app.routers import auth, permits, documents, admin_tenants, public_tenants
from app.middleware.security import SecurityMiddleware
from app.middleware.tenant import TenantMiddleware
from app.middleware.audit import AuditMiddleware


# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events
    """
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    
    # Skip database table creation - tables already exist
    logger.info("Skipping database table creation (tables already exist)")
    
    # Verify external services connectivity
    try:
        # Test MinIO connection
        from app.services.storage_service import StorageService
        storage_service = StorageService()
        logger.info("MinIO connection verified")
        
        # Initialize optimized vector service with native multi-tenancy
        try:
            from app.services.service_factory import VectorServiceFactory
            vector_service = VectorServiceFactory.get_vector_service()
            service_info = VectorServiceFactory.get_service_info()

            if vector_service and vector_service.client:
                logger.info(f"Vector Service initialized: {service_info['service_type']}")
                logger.info(f"Performance: {service_info['performance_profile']}")
                logger.info(f"Security: {service_info['security_level']}")
            else:
                logger.warning("Vector service unavailable - running in PostgreSQL-only mode")
        except Exception as weaviate_error:
            logger.warning(f"Vector service initialization failed: {weaviate_error}")
        
    except Exception as e:
        logger.warning(f"External service connectivity issue: {e}")
        # Don't fail startup, but log the warning
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.app_name}")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Sistema HSE Backend Multi-Agente Enterprise per gestione permessi di lavoro industriali",
    docs_url="/api/docs" if settings.debug else None,
    redoc_url="/api/redoc" if settings.debug else None,
    lifespan=lifespan,
    # Add security schemes for Swagger UI
    openapi_tags=[
        {"name": "Authentication", "description": "Authentication and authorization"},
        {"name": "Work Permits", "description": "Work permit management"},
        {"name": "Documents", "description": "Document management"},
        {"name": "Admin", "description": "Administrative operations"},
        {"name": "Public", "description": "Public endpoints"}
    ]
)

# Add security scheme for JWT Bearer tokens
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    # Add Bearer token security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT token. After login, use the token from the response."
        }
    }
    
    # Apply security globally to all endpoints that need auth
    # This can be overridden per endpoint if needed
    for path_item in openapi_schema["paths"].values():
        for operation in path_item.values():
            if isinstance(operation, dict) and "operationId" in operation:
                # Skip public endpoints
                if any(tag in operation.get("tags", []) for tag in ["Authentication"]):
                    continue
                # Skip specific public operations
                if operation.get("operationId") in ["root", "health_check", "health_check_options", "system_info", "login"]:
                    continue
                # Add security requirement
                if "security" not in operation:
                    operation["security"] = [{"HTTPBearer": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Add custom middleware (order matters!)
# These are added first so they execute after CORS
app.add_middleware(AuditMiddleware)
app.add_middleware(TenantMiddleware)
app.add_middleware(SecurityMiddleware)

# Add CORS middleware LAST so it runs FIRST
# This ensures CORS headers are added before any other middleware runs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Include routers
app.include_router(auth.router)
app.include_router(permits.router)
app.include_router(documents.router)
app.include_router(admin_tenants.router)
app.include_router(public_tenants.router)


@app.get("/")
async def root():
    """
    Root endpoint with API information
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "docs_url": "/api/docs" if settings.debug else "Documentation disabled in production"
    }


@app.options("/health")
async def health_check_options():
    """
    OPTIONS handler for health check endpoint
    """
    return {"message": "OK"}


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app_version,
        "environment": settings.environment
    }
    
    # Check database connectivity
    try:
        from app.config.database import SessionLocal
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        health_status["database"] = "connected"
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check Weaviate connectivity (disabled for now)
    try:
        # Temporarily disabled to avoid startup issues
        health_status["weaviate"] = "disabled"
    except Exception as e:
        health_status["weaviate"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check MinIO connectivity
    try:
        from app.services.storage_service import StorageService
        storage_service = StorageService()
        health_status["minio"] = "connected"
    except Exception as e:
        health_status["minio"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Return appropriate status code
    status_code = 200 if health_status["status"] == "healthy" else 503
    return JSONResponse(content=health_status, status_code=status_code)


@app.get("/api/v1/system/info")
async def system_info():
    """
    System information endpoint (for monitoring)
    """
    return {
        "application": {
            "name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
            "debug": settings.debug
        },
        "features": {
            "multi_tenant": True,
            "ai_analysis": True,
            "vector_search": True,
            "rbac": True,
            "audit_logging": True
        },
        "ai_provider": {
            "provider": getattr(settings, 'ai_provider', 'gemini'),
            "model": getattr(settings, 'gemini_model', 'gemini-1.5-pro') if getattr(settings, 'ai_provider', 'gemini') == 'gemini' else getattr(settings, 'openai_model', 'gpt-4')
        },
        "limits": {
            "max_tenants": settings.max_tenants,
            "default_user_limit": settings.default_tenant_user_limit,
            "default_document_limit": settings.default_tenant_document_limit,
            "max_file_size_mb": settings.max_file_size_mb
        },
        "timestamp": datetime.utcnow().isoformat()
    }


# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handle HTTP exceptions with consistent format
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": "HTTPException",
                "message": exc.detail,
                "status_code": exc.status_code,
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url.path)
            }
        }
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """
    Handle ValueError exceptions
    """
    logger.error(f"ValueError in {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "type": "ValueError",
                "message": str(exc),
                "status_code": 400,
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url.path)
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle all other exceptions
    """
    logger.error(f"Unhandled exception in {request.url.path}: {str(exc)}", exc_info=True)
    
    # Don't expose internal errors in production
    if settings.environment == "production":
        message = "Internal server error"
    else:
        message = str(exc)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "type": "InternalServerError",
                "message": message,
                "status_code": 500,
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url.path)
            }
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info"
    )