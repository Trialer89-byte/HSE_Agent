from sqlalchemy import Column, Integer, String, Text, JSON, Float, DateTime, ForeignKey, Boolean
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
    equipment = Column(JSON, default=[])
    risk_level = Column(String(20), default="medium")
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    
    # Risk Mitigation Actions (new field)
    risk_mitigation_actions = Column(JSON, default=[])
    
    # AI Analysis Results
    ai_analysis = Column(JSON, default={})
    ai_version = Column(String(50))
    
    # Structured AI Results
    action_items = Column(JSON, default=[])
    
    # Workflow
    status = Column(String(50), default="draft", index=True)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    approved_by = Column(Integer, ForeignKey("users.id"))
    
    # Timestamps
    analyzed_at = Column(DateTime)
    valid_from = Column(DateTime)
    valid_until = Column(DateTime)
    
    # Extensibility
    attachments = Column(JSON, default=[])
    custom_fields = Column(JSON, default={})
    
    # Relationships
    tenant = relationship("Tenant", back_populates="work_permits")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_permits")
    approver = relationship("User", foreign_keys=[approved_by], back_populates="approved_permits")
    
    def __repr__(self):
        return f"<WorkPermit(id={self.id}, title='{self.title}', status='{self.status}')>"
    
    @property
    def duration_hours(self) -> int:
        """Calculate duration in hours from start_date to end_date"""
        if self.start_date and self.end_date:
            duration = self.end_date - self.start_date
            return int(duration.total_seconds() / 3600)
        return 0
    
    def to_dict(self):
        """Convert permit to dictionary for AI processing"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "dpi_required": self.dpi_required,
            "work_type": self.work_type,
            "location": self.location,
            "equipment": self.equipment,
            "duration_hours": self.duration_hours,  # Now calculated property
            "risk_level": self.risk_level,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "risk_mitigation_actions": self.risk_mitigation_actions,
            "custom_fields": self.custom_fields
        }