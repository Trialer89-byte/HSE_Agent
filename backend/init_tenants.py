#!/usr/bin/env python3
"""
Script to initialize sample tenants for testing multi-tenant functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.config.database import SessionLocal, engine
from app.models.tenant import Tenant, DeploymentMode, SubscriptionPlan
from app.models.user import User
from app.models.base import Base
from app.core.security import get_password_hash
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_sample_tenants():
    """
    Create sample tenants for testing
    """
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Sample SaaS Tenant
        saas_tenant = Tenant(
            name="demo_company",
            display_name="Demo Company Ltd",
            domain="demo.hse-system.com",
            deployment_mode=DeploymentMode.SAAS,
            subscription_plan=SubscriptionPlan.PROFESSIONAL,
            max_users=50,
            max_documents=500,
            max_storage_gb=5,
            contact_email="admin@democompany.com",
            settings={
                "max_file_size_mb": 25,
                "allowed_file_types": [".pdf", ".docx", ".doc"],
                "ai_analysis_enabled": True,
                "require_approval": True
            },
            custom_branding={
                "logo_url": "https://democompany.com/logo.png",
                "primary_color": "#1976d2",  
                "secondary_color": "#424242"
            }
        )
        
        # Sample On-Premise Tenant (Enterprise)
        onprem_tenant = Tenant(
            name="enterprise_corp",
            display_name="Enterprise Corporation",
            domain="enterprise.hse-system.com",
            deployment_mode=DeploymentMode.ON_PREMISE,
            database_url="postgresql://enterprise:password@enterprise-db:5432/hse_enterprise",
            subscription_plan=SubscriptionPlan.ENTERPRISE,
            max_users=500,
            max_documents=10000,
            max_storage_gb=100,
            contact_email="admin@enterprise-corp.com",
            enforce_2fa=True,
            allowed_ip_ranges=["192.168.1.0/24", "10.0.0.0/8"],
            session_timeout_minutes=240,  # 4 hours
            settings={
                "max_file_size_mb": 100,
                "allowed_file_types": [".pdf", ".docx", ".doc", ".xlsx", ".pptx"],
                "ai_analysis_enabled": True,
                "require_approval": True,
                "audit_retention_days": 2555  # 7 years
            }
        )
        
        # Sample Small Business Tenant
        small_biz_tenant = Tenant(
            name="small_manufacturing",
            display_name="Small Manufacturing Co",
            domain="smallmfg.hse-system.com",
            deployment_mode=DeploymentMode.SAAS,
            subscription_plan=SubscriptionPlan.BASIC,
            max_users=10,
            max_documents=100,
            max_storage_gb=2,
            contact_email="manager@smallmfg.com",
            settings={
                "max_file_size_mb": 10,
                "allowed_file_types": [".pdf", ".docx"],
                "ai_analysis_enabled": True,
                "require_approval": False  # Simplified workflow for small business
            }
        )
        
        # Add tenants to database
        for tenant in [saas_tenant, onprem_tenant, small_biz_tenant]:
            existing = db.query(Tenant).filter_by(name=tenant.name).first()
            if not existing:
                db.add(tenant)
                logger.info(f"Created tenant: {tenant.name}")
            else:
                logger.info(f"Tenant already exists: {tenant.name}")
        
        db.commit()
        
        # Create super admin user (not tied to any specific tenant)
        super_admin = db.query(User).filter_by(username="superadmin").first()
        if not super_admin:
            super_admin = User(
                username="superadmin",
                email="superadmin@hse-system.com",
                password_hash=get_password_hash("SuperAdmin123!"),
                first_name="Super",
                last_name="Admin",
                role="super_admin",
                tenant_id=saas_tenant.id,  # Assign to demo tenant for now
                is_active=True,
                is_verified=True
            )
            db.add(super_admin)
            db.commit()
            logger.info("Created super admin user")
        else:
            logger.info("Super admin user already exists")
        
        # Create sample users for each tenant
        create_sample_users(db)
        
        logger.info("Sample tenants and users created successfully!")
        
    except Exception as e:
        logger.error(f"Error creating sample tenants: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def create_sample_users(db: Session):
    """
    Create sample users for each tenant
    """
    tenants = db.query(Tenant).all()
    
    for tenant in tenants:
        # Check if tenant already has users
        existing_users = db.query(User).filter_by(tenant_id=tenant.id).count()
        if existing_users > 1:  # Skip if already has users (besides super admin)
            continue
        
        # Admin user for tenant
        admin_user = User(
            username=f"admin_{tenant.name}",
            email=f"admin@{tenant.name}.com",
            password_hash=get_password_hash("Admin123!"),
            first_name="Tenant",
            last_name="Admin",
            role="admin",
            tenant_id=tenant.id,
            is_active=True,
            is_verified=True
        )
        
        # Regular user for tenant
        user = User(
            username=f"user_{tenant.name}",
            email=f"user@{tenant.name}.com",
            password_hash=get_password_hash("User123!"),
            first_name="Regular",
            last_name="User",
            role="user",
            tenant_id=tenant.id,
            department="Safety",
            is_active=True,
            is_verified=True
        )
        
        # Viewer user for tenant
        viewer = User(
            username=f"viewer_{tenant.name}",
            email=f"viewer@{tenant.name}.com",
            password_hash=get_password_hash("Viewer123!"),
            first_name="View",
            last_name="Only",
            role="viewer",
            tenant_id=tenant.id,
            department="Management",
            is_active=True,
            is_verified=True
        )
        
        db.add_all([admin_user, user, viewer])
        logger.info(f"Created sample users for tenant: {tenant.name}")
    
    db.commit()


if __name__ == "__main__":
    create_sample_tenants()
    print("\n=== Multi-Tenant System Initialized ===")
    print("\nSample Tenants Created:")
    print("1. Demo Company (SaaS) - demo.hse-system.com")
    print("2. Enterprise Corp (On-Premise) - enterprise.hse-system.com") 
    print("3. Small Manufacturing (SaaS) - smallmfg.hse-system.com")
    print("\nSample Users Created:")
    print("- superadmin / SuperAdmin123! (Super Admin)")
    print("- admin_[tenant] / Admin123! (Tenant Admin)")
    print("- user_[tenant] / User123! (Regular User)")
    print("- viewer_[tenant] / Viewer123! (Viewer)")
    print("\nTo test multi-tenancy:")
    print("1. Use X-Tenant-Domain header or subdomain routing")
    print("2. Login with tenant-specific users")
    print("3. Data will be automatically isolated by tenant")