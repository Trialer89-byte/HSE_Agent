from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.config.database import get_db
from app.models.tenant import Tenant
from app.schemas.tenant import TenantInfo

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/public/tenants",
    tags=["public-tenants"]
)


@router.get("/by-domain", response_model=TenantInfo)
async def get_tenant_by_domain(
    domain: str = Query(..., description="Domain name to lookup tenant"),
    db: Session = Depends(get_db)
):
    """
    Get tenant information by domain (public endpoint for frontend)
    """
    tenant = db.query(Tenant).filter(
        Tenant.domain == domain,
        Tenant.is_active == True
    ).first()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found or inactive"
        )
    
    return TenantInfo(
        id=tenant.id,
        display_name=tenant.display_name,
        domain=tenant.domain,
        custom_branding=tenant.custom_branding or {},
        is_active=tenant.is_active,
        deployment_mode=tenant.deployment_mode
    )


@router.get("/by-subdomain", response_model=TenantInfo)
async def get_tenant_by_subdomain(
    subdomain: str = Query(..., description="Subdomain to lookup tenant"),
    db: Session = Depends(get_db)
):
    """
    Get tenant information by subdomain (public endpoint for frontend)
    """
    # Look for tenant with matching subdomain pattern
    tenant = db.query(Tenant).filter(
        Tenant.domain.like(f"{subdomain}.%"),
        Tenant.is_active == True
    ).first()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found or inactive"
        )
    
    return TenantInfo(
        id=tenant.id,
        display_name=tenant.display_name,
        domain=tenant.domain,
        custom_branding=tenant.custom_branding or {},
        is_active=tenant.is_active,
        deployment_mode=tenant.deployment_mode
    )


@router.get("/validate", response_model=dict)
async def validate_tenant_access(
    domain: Optional[str] = Query(None, description="Domain to validate"),
    subdomain: Optional[str] = Query(None, description="Subdomain to validate"),
    db: Session = Depends(get_db)
):
    """
    Validate tenant access (public endpoint for frontend routing)
    """
    if not domain and not subdomain:
        return {
            "valid": False,
            "message": "Domain or subdomain required"
        }
    
    query = db.query(Tenant).filter(Tenant.is_active == True)
    
    if domain:
        tenant = query.filter(Tenant.domain == domain).first()
    elif subdomain:
        tenant = query.filter(Tenant.domain.like(f"{subdomain}.%")).first()
    
    if tenant:
        return {
            "valid": True,
            "tenant_id": tenant.id,
            "display_name": tenant.display_name,
            "deployment_mode": tenant.deployment_mode.value
        }
    else:
        return {
            "valid": False,
            "message": "Tenant not found or inactive"
        }