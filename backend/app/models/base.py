from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql import func
from datetime import datetime

from app.config.database import Base


class TimestampMixin:
    """
    Mixin to add created_at and updated_at timestamps
    """
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)


class TenantMixin:
    """
    Mixin to add tenant_id for multi-tenant isolation
    """
    @declared_attr
    def tenant_id(cls):
        return Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)