from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class DeploymentModeEnum(str, Enum):
    SAAS = "saas"
    ON_PREMISE = "on_premise"
    HYBRID = "hybrid"


class SubscriptionPlanEnum(str, Enum):
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class TenantBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, pattern=r"^[a-zA-Z0-9_-]+$")
    display_name: str = Field(..., min_length=2, max_length=255)
    domain: Optional[str] = Field(None, pattern=r"^[a-zA-Z0-9.-]+$")
    contact_email: Optional[str] = Field(None, pattern=r"^[^@]+@[^@]+\.[^@]+$")


class TenantCreate(TenantBase):
    deployment_mode: DeploymentModeEnum = DeploymentModeEnum.SAAS
    database_url: Optional[str] = None
    subscription_plan: SubscriptionPlanEnum = SubscriptionPlanEnum.BASIC
    max_users: int = Field(default=100, ge=1, le=10000)
    max_documents: int = Field(default=1000, ge=1, le=100000)
    max_storage_gb: int = Field(default=10, ge=1, le=1000)
    settings: Optional[Dict[str, Any]] = None
    custom_branding: Optional[Dict[str, Any]] = None
    
    @field_validator('database_url')
    @classmethod
    def validate_database_url(cls, v, info):
        deployment_mode = info.data.get('deployment_mode')
        if deployment_mode in [DeploymentModeEnum.ON_PREMISE, DeploymentModeEnum.HYBRID]:
            if not v:
                raise ValueError('database_url is required for on-premise and hybrid deployments')
        return v


class TenantUpdate(BaseModel):
    display_name: Optional[str] = Field(None, min_length=2, max_length=255)
    domain: Optional[str] = Field(None, pattern=r"^[a-zA-Z0-9.-]+$")
    contact_email: Optional[str] = Field(None, pattern=r"^[^@]+@[^@]+\.[^@]+$")
    database_url: Optional[str] = None
    subscription_plan: Optional[SubscriptionPlanEnum] = None
    max_users: Optional[int] = Field(None, ge=1, le=10000)
    max_documents: Optional[int] = Field(None, ge=1, le=100000)
    max_storage_gb: Optional[int] = Field(None, ge=1, le=1000)
    settings: Optional[Dict[str, Any]] = None
    custom_branding: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    trial_expires_at: Optional[datetime] = None
    enforce_2fa: Optional[bool] = None
    allowed_ip_ranges: Optional[List[str]] = None
    session_timeout_minutes: Optional[int] = Field(None, ge=5, le=1440)  # 5 min to 24 hours


class TenantResponse(TenantBase):
    id: int
    deployment_mode: DeploymentModeEnum
    subscription_plan: SubscriptionPlanEnum
    max_users: int
    max_documents: int
    max_storage_gb: int
    is_active: bool
    trial_expires_at: Optional[datetime] = None
    enforce_2fa: bool
    session_timeout_minutes: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TenantWithStats(TenantResponse):
    user_count: int = 0
    document_count: int = 0
    storage_used_gb: float = 0.0
    
    @property
    def usage_stats(self) -> Dict[str, Any]:
        return {
            "users": {
                "current": self.user_count,
                "limit": self.max_users,
                "percentage": round((self.user_count / self.max_users) * 100, 1) if self.max_users > 0 else 0
            },
            "documents": {
                "current": self.document_count,
                "limit": self.max_documents,
                "percentage": round((self.document_count / self.max_documents) * 100, 1) if self.max_documents > 0 else 0
            },
            "storage": {
                "current_gb": self.storage_used_gb,
                "limit_gb": self.max_storage_gb,
                "percentage": round((self.storage_used_gb / self.max_storage_gb) * 100, 1) if self.max_storage_gb > 0 else 0
            }
        }


class TenantSettings(BaseModel):
    """
    Tenant-specific configuration settings
    """
    # File upload settings
    max_file_size_mb: int = Field(default=50, ge=1, le=500)
    allowed_file_types: List[str] = Field(default=[".pdf", ".docx", ".doc", ".txt"])
    
    # AI Analysis settings
    ai_analysis_enabled: bool = True
    ai_provider: str = Field(default="gemini", pattern=r"^(gemini|openai|anthropic)$")
    
    # Security settings
    require_approval: bool = True
    audit_retention_days: int = Field(default=365, ge=30, le=2555)  # 30 days to 7 years
    
    # Workflow settings
    auto_assign_permits: bool = False
    notification_settings: Dict[str, bool] = Field(default={
        "email_notifications": True,
        "sms_notifications": False,
        "slack_integration": False
    })
    
    # Custom fields for permits
    custom_permit_fields: List[Dict[str, Any]] = Field(default=[])
    
    # Branding
    logo_url: Optional[str] = None
    primary_color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    secondary_color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")


class TenantInfo(BaseModel):
    """
    Public tenant information (for login/registration pages)
    """
    id: int
    display_name: str
    domain: Optional[str] = None
    custom_branding: Dict[str, Any] = {}
    is_active: bool
    deployment_mode: DeploymentModeEnum
    
    class Config:
        from_attributes = True