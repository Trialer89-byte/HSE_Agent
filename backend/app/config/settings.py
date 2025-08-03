from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Application
    app_name: str = "HSE Enterprise System"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False
    
    # Database
    database_url: str
    db_pool_size: int = 20
    db_max_overflow: int = 40
    
    # Redis
    redis_url: str
    redis_password: str = ""
    
    # MinIO
    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    minio_bucket_name: str = "hse-documents"
    minio_secure: bool = False
    
    # Weaviate
    weaviate_url: str
    weaviate_api_key: str = ""
    
    # Security
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # AI Provider Configuration
    ai_provider: str = "gemini"  # "openai" or "gemini"
    
    # OpenAI (fallback)
    openai_api_key: str = ""
    openai_model: str = "gpt-4-turbo-preview"
    
    # Gemini
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-pro"
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000"]
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    
    # File Upload
    max_file_size_mb: int = 50
    allowed_file_types: List[str] = [".pdf", ".docx", ".doc", ".txt"]
    
    # Multi-tenant
    max_tenants: int = 1000
    default_tenant_user_limit: int = 100
    default_tenant_document_limit: int = 1000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()