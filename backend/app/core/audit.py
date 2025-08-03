from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import Request
from sqlalchemy.orm import Session

from app.models.audit import AuditLog
from app.models.user import User


class AuditService:
    """
    Service for comprehensive audit logging
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    async def log_action(
        self,
        user_id: Optional[int],
        tenant_id: int,
        action: str,
        resource_type: str,
        resource_id: Optional[int] = None,
        resource_name: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        extra_data: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        api_endpoint: Optional[str] = None,
        severity: str = "info",
        category: Optional[str] = None
    ):
        """
        Log an action to the audit trail
        """
        # Get username if user_id provided
        username = None
        if user_id:
            user = self.db.query(User).filter(User.id == user_id).first()
            username = user.username if user else f"user_id_{user_id}"
        
        audit_log = AuditLog(
            tenant_id=tenant_id,
            user_id=user_id,
            username=username,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            old_values=old_values or {},
            new_values=new_values or {},
            extra_data=extra_data or {},
            ip_address=ip_address,
            user_agent=user_agent,
            api_endpoint=api_endpoint,
            severity=severity,
            category=category
        )
        
        self.db.add(audit_log)
        self.db.commit()
        
        return audit_log
    
    async def log_authentication(
        self,
        tenant_id: int,
        username: str,
        success: bool,
        ip_address: str,
        user_agent: str,
        failure_reason: Optional[str] = None
    ):
        """
        Log authentication attempts
        """
        action = "auth.login_success" if success else "auth.login_failed"
        extra_data = {}
        
        if not success and failure_reason:
            extra_data["failure_reason"] = failure_reason
        
        await self.log_action(
            user_id=None,
            tenant_id=tenant_id,
            action=action,
            resource_type="authentication",
            extra_data=extra_data,
            ip_address=ip_address,
            user_agent=user_agent,
            severity="warning" if not success else "info",
            category="authentication"
        )
    
    async def log_data_access(
        self,
        user: User,
        resource_type: str,
        resource_id: int,
        action: str = "read",
        extra_data: Optional[Dict[str, Any]] = None
    ):
        """
        Log data access for compliance
        """
        await self.log_action(
            user_id=user.id,
            tenant_id=user.tenant_id,
            action=f"data.{action}",
            resource_type=resource_type,
            resource_id=resource_id,
            extra_data=extra_data,
            category="data_access"
        )
    
    async def log_ai_analysis(
        self,
        user: User,
        permit_id: int,
        analysis_results: Dict[str, Any],
        confidence_score: float,
        processing_time: float
    ):
        """
        Log AI analysis operations
        """
        extra_data = {
            "confidence_score": confidence_score,
            "processing_time_seconds": processing_time,
            "agents_used": analysis_results.get("agents_involved", []),
            "analysis_version": analysis_results.get("ai_version")
        }
        
        await self.log_action(
            user_id=user.id,
            tenant_id=user.tenant_id,
            action="ai.analysis_completed",
            resource_type="work_permit",
            resource_id=permit_id,
            extra_data=extra_data,
            category="ai_analysis"
        )
    
    async def log_security_event(
        self,
        tenant_id: int,
        event_type: str,
        description: str,
        ip_address: str,
        severity: str = "warning",
        extra_data: Optional[Dict[str, Any]] = None
    ):
        """
        Log security events
        """
        await self.log_action(
            user_id=None,
            tenant_id=tenant_id,
            action=f"security.{event_type}",
            resource_type="security",
            resource_name=description,
            extra_data=extra_data,
            ip_address=ip_address,
            severity=severity,
            category="security"
        )


def get_client_ip(request: Request) -> str:
    """
    Extract client IP address from request
    """
    # Check for forwarded headers first (proxy/load balancer)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    # Check other common headers
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct connection
    return str(request.client.host) if request.client else "unknown"


def get_user_agent(request: Request) -> str:
    """
    Extract user agent from request
    """
    return request.headers.get("User-Agent", "unknown")