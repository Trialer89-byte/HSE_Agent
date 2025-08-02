from sqlalchemy import Column, Integer, String, Boolean, JSON, Text
from sqlalchemy.orm import relationship

from app.config.database import Base
from .base import TimestampMixin


class Tenant(Base, TimestampMixin):
    __tablename__ = "tenants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    domain = Column(String(255), unique=True)
    settings = Column(JSON, default={})
    subscription_plan = Column(String(50), default="basic")
    max_users = Column(Integer, default=100)
    max_documents = Column(Integer, default=1000)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    work_permits = relationship("WorkPermit", back_populates="tenant", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="tenant", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="tenant", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Tenant(id={self.id}, name='{self.name}')>"