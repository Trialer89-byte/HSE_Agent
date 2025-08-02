from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import logging
from datetime import datetime

from app.config.settings import settings
from app.config.database import Base, engine
from app.routers import auth, permits
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
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise
    
    # Verify external services connectivity
    try:
        # Test Weaviate connection
        from app.services.vector_service import VectorService
        vector_service = VectorService()
        logger.info("Weaviate connection verified")
        
        # Test MinIO connection
        from app.services.storage_service import StorageService
        storage_service = StorageService()
        logger.info("MinIO connection verified")
        
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
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Add custom middleware (order matters!)
app.add_middleware(AuditMiddleware)  # Must be first to capture all requests
app.add_middleware(TenantMiddleware)
app.add_middleware(SecurityMiddleware)

# Include routers
app.include_router(auth.router)
app.include_router(permits.router)


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
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        health_status["database"] = "connected"
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check Weaviate connectivity
    try:
        from app.services.vector_service import VectorService
        vector_service = VectorService()
        # Simple connectivity test
        health_status["weaviate"] = "connected"
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