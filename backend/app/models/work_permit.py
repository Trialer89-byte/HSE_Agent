from sqlalchemy import Column, Integer, String, Text, JSON, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.config.database import Base
from .base import TimestampMixin, TenantMixin


class WorkPermit(Base, TimestampMixin, TenantMixin):
    __tablename__ = "work_permits"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Fields
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    dpi_required = Column(JSON, default=[])
    
    # Extended Fields
    work_type = Column(String(100))
    location = Column(String(255))
    duration_hours = Column(Integer)
    priority_level = Column(String(20), default="medium")
    
    # AI Analysis Results
    ai_analysis = Column(JSON, default={})
    ai_confidence = Column(Float, default=0.0)
    ai_version = Column(String(20))
    
    # Structured AI Results
    content_analysis = Column(JSON, default={})
    risk_assessment = Column(JSON, default={})
    compliance_check = Column(JSON, default={})
    dpi_recommendations = Column(JSON, default={})
    action_items = Column(JSON, default=[])
    
    # Workflow
    status = Column(String(50), default="draft", index=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    approved_by = Column(Integer, ForeignKey("users.id"))
    
    # Timestamps
    analyzed_at = Column(DateTime)
    
    # Extensibility
    custom_fields = Column(JSON, default={})
    attachments = Column(JSON, default=[])
    tags = Column(JSON, default=[])
    
    # Relationships
    tenant = relationship("Tenant", back_populates="work_permits")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_permits")
    approver = relationship("User", foreign_keys=[approved_by], back_populates="approved_permits")
    
    def __repr__(self):
        return f"<WorkPermit(id={self.id}, title='{self.title}', status='{self.status}')>"
    
    def to_dict(self):
        """Convert permit to dictionary for AI processing"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "dpi_required": self.dpi_required,
            "work_type": self.work_type,
            "location": self.location,
            "duration_hours": self.duration_hours,
            "priority_level": self.priority_level,
            "custom_fields": self.custom_fields,
            "tags": self.tags,
            # Include frequently used fields from custom_fields for agent compatibility
            "equipment": self.custom_fields.get("equipment", "") if self.custom_fields else "",
            "workers_count": self.custom_fields.get("workers_count", "") if self.custom_fields else "",
            "identified_risks": self.custom_fields.get("identified_risks", []) if self.custom_fields else [],
            "control_measures": self.custom_fields.get("control_measures", []) if self.custom_fields else []
        }