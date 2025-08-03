from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import relationship

from app.config.database import Base
from .base import TenantMixin


class AuditLog(Base, TenantMixin):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Who & When
    user_id = Column(Integer, ForeignKey("users.id"))
    username = Column(String(100))
    session_id = Column(String(255))
    
    # What & Where
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(Integer)
    resource_name = Column(String(255))
    
    # Details
    old_values = Column(JSON)
    new_values = Column(JSON)
    extra_data = Column(JSON, default={})
    
    # Context
    ip_address = Column(INET)
    user_agent = Column(Text)
    api_endpoint = Column(String(255))
    
    # Classification
    severity = Column(String(20), default="info")
    category = Column(String(50))
    
    # Timestamp
    created_at = Column(DateTime, server_default="NOW()", nullable=False, index=True)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="audit_logs")
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', user='{self.username}')>"