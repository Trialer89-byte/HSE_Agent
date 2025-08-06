from sqlalchemy import Column, Integer, String, Boolean, JSON, Text, DateTime, Enum
from sqlalchemy.orm import relationship
import enum

from app.config.database import Base
from .base import TimestampMixin


class DeploymentMode(enum.Enum):
    SAAS = "saas"
    ON_PREMISE = "on_premise"
    HYBRID = "hybrid"


class SubscriptionPlan(enum.Enum):
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class Tenant(Base, TimestampMixin):
    __tablename__ = "tenants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    display_name = Column(String(255), nullable=False)
    domain = Column(String(255), unique=True)
    
    # Deployment configuration
    deployment_mode = Column(Enum(DeploymentMode), default=DeploymentMode.SAAS)
    database_url = Column(String(500))  # For on-premise deployments
    
    # Subscription and limits
    subscription_plan = Column(Enum(SubscriptionPlan), default=SubscriptionPlan.BASIC)
    max_users = Column(Integer, default=100)
    max_documents = Column(Integer, default=1000)
    max_storage_gb = Column(Integer, default=10)
    
    # Configuration
    settings = Column(JSON, default={})
    custom_branding = Column(JSON, default={})
    
    # Status and metadata
    is_active = Column(Boolean, default=True)
    trial_expires_at = Column(DateTime)
    contact_email = Column(String(255))
    
    # Security settings
    enforce_2fa = Column(Boolean, default=False)
    allowed_ip_ranges = Column(JSON, default=[])
    session_timeout_minutes = Column(Integer, default=480)  # 8 hours
    
    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    work_permits = relationship("WorkPermit", back_populates="tenant", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="tenant", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="tenant", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Tenant(id={self.id}, name='{self.name}')>"