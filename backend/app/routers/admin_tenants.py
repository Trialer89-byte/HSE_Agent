from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.config.database import get_db
from app.models.tenant import Tenant, DeploymentMode, SubscriptionPlan
from app.models.user import User
from app.schemas.tenant import (
    TenantCreate, TenantUpdate, TenantResponse, 
    TenantWithStats, DeploymentModeEnum, SubscriptionPlanEnum
)
from app.core.permissions import require_super_admin
from app.services.tenant_database_service import tenant_db_service
from app.core.security import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/admin/tenants",
    tags=["admin-tenants"],
    dependencies=[Depends(require_super_admin)]
)


@router.post("/", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    tenant_data: TenantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new tenant (Super Admin only)
    """
    # Check if tenant name or domain already exists
    existing = db.query(Tenant).filter(
        (Tenant.name == tenant_data.name) | 
        (Tenant.domain == tenant_data.domain)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Tenant name or domain already exists"
        )
    
    # Create tenant
    tenant = Tenant(
        name=tenant_data.name,
        display_name=tenant_data.display_name,
        domain=tenant_data.domain,
        deployment_mode=tenant_data.deployment_mode,
        database_url=tenant_data.database_url,
        subscription_plan=tenant_data.subscription_plan,
        max_users=tenant_data.max_users,
        max_documents=tenant_data.max_documents,
        max_storage_gb=tenant_data.max_storage_gb,
        contact_email=tenant_data.contact_email,
        settings=tenant_data.settings or {},
        custom_branding=tenant_data.custom_branding or {}
    )
    
    try:
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        
        # Initialize database for on-premise deployments
        if tenant.deployment_mode in [DeploymentMode.ON_PREMISE, DeploymentMode.HYBRID]:
            if tenant.database_url:
                success = tenant_db_service.initialize_tenant_database(tenant)
                if not success:
                    logger.warning(f"Failed to initialize database for tenant {tenant.id}")
        
        logger.info(f"Created tenant {tenant.id} by super admin {current_user.id}")
        return tenant
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create tenant: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create tenant"
        )


@router.get("/", response_model=List[TenantWithStats])
async def list_tenants(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    deployment_mode: Optional[DeploymentModeEnum] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    List all tenants with statistics (Super Admin only)
    """
    query = db.query(Tenant)
    
    # Apply filters
    if deployment_mode:
        query = query.filter(Tenant.deployment_mode == deployment_mode.value)
    if is_active is not None:
        query = query.filter(Tenant.is_active == is_active)
    
    tenants = query.offset(skip).limit(limit).all()
    
    # Add statistics to each tenant
    tenant_stats = []
    for tenant in tenants:
        user_count = db.query(User).filter_by(tenant_id=tenant.id).count()
        
        stats = TenantWithStats(
            **tenant.__dict__,
            user_count=user_count,
            document_count=0,  # TODO: Add document count
            storage_used_gb=0  # TODO: Add storage calculation
        )
        tenant_stats.append(stats)
    
    return tenant_stats


@router.get("/{tenant_id}", response_model=TenantWithStats)
async def get_tenant(
    tenant_id: int,
    db: Session = Depends(get_db)
):
    """
    Get tenant by ID with statistics (Super Admin only)
    """
    tenant = db.query(Tenant).filter_by(id=tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    # Add statistics
    user_count = db.query(User).filter_by(tenant_id=tenant.id).count()
    
    return TenantWithStats(
        **tenant.__dict__,
        user_count=user_count,
        document_count=0,  # TODO: Add document count
        storage_used_gb=0  # TODO: Add storage calculation
    )


@router.put("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: int,
    tenant_data: TenantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update tenant (Super Admin only)
    """
    tenant = db.query(Tenant).filter_by(id=tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    # Update fields
    update_data = tenant_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tenant, field, value)
    
    try:
        db.commit()
        db.refresh(tenant)
        
        logger.info(f"Updated tenant {tenant_id} by super admin {current_user.id}")
        return tenant
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update tenant {tenant_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update tenant"
        )


@router.delete("/{tenant_id}")
async def delete_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete tenant (Super Admin only) - Use with extreme caution!
    """
    tenant = db.query(Tenant).filter_by(id=tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    try:
        # Clean up tenant-specific database connections
        tenant_db_service.cleanup_tenant_connection(tenant_id)
        
        # Delete tenant (cascades to users, documents, etc.)
        db.delete(tenant)
        db.commit()
        
        logger.warning(f"Deleted tenant {tenant_id} by super admin {current_user.id}")
        return {"message": "Tenant deleted successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete tenant {tenant_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete tenant"
        )


@router.post("/{tenant_id}/activate")
async def activate_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Activate tenant (Super Admin only)
    """
    tenant = db.query(Tenant).filter_by(id=tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    tenant.is_active = True
    db.commit()
    
    logger.info(f"Activated tenant {tenant_id} by super admin {current_user.id}")
    return {"message": "Tenant activated successfully"}


@router.post("/{tenant_id}/deactivate")
async def deactivate_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deactivate tenant (Super Admin only)
    """
    tenant = db.query(Tenant).filter_by(id=tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    tenant.is_active = False
    db.commit()
    
    logger.info(f"Deactivated tenant {tenant_id} by super admin {current_user.id}")
    return {"message": "Tenant deactivated successfully"}


@router.get("/{tenant_id}/validate-database")
async def validate_tenant_database(
    tenant_id: int,
    db: Session = Depends(get_db)
):
    """
    Validate tenant database connectivity (Super Admin only)
    """
    tenant = db.query(Tenant).filter_by(id=tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    if tenant.deployment_mode == DeploymentMode.SAAS:
        return {"status": "valid", "message": "SaaS tenant uses shared database"}
    
    is_valid = tenant_db_service.validate_tenant_database(tenant)
    
    return {
        "status": "valid" if is_valid else "invalid",
        "message": "Database connection successful" if is_valid else "Database connection failed"
    }