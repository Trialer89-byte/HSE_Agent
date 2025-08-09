#!/usr/bin/env python3
"""
Script to initialize demo users for testing
Creates users matching the login page credentials:
- admin / Admin123!
- user / User123!
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


def create_demo_users():
    """
    Create demo users for testing
    """
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Create demo tenant if not exists
        demo_tenant = db.query(Tenant).filter(Tenant.domain == "demo.hse-system.com").first()
        if not demo_tenant:
            demo_tenant = Tenant(
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
                },
                is_active=True
            )
            db.add(demo_tenant)
            db.commit()
            logger.info(f"Created demo tenant: {demo_tenant.name}")
        else:
            logger.info(f"Demo tenant already exists: {demo_tenant.name}")
        
        # Create admin user with exact credentials from login page
        admin_user = db.query(User).filter(
            User.username == "admin",
            User.tenant_id == demo_tenant.id
        ).first()
        
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@demo.hse-system.com",
                password_hash=get_password_hash("Admin123!"),
                first_name="Demo",
                last_name="Admin",
                role="admin",
                tenant_id=demo_tenant.id,
                department="Management",
                is_active=True,
                is_verified=True
            )
            db.add(admin_user)
            db.commit()
            logger.info("Created admin user: admin / Admin123!")
        else:
            # Update password to match expected credentials
            admin_user.password_hash = get_password_hash("Admin123!")
            db.commit()
            logger.info("Updated admin user password to: Admin123!")
        
        # Create regular user with exact credentials from login page
        regular_user = db.query(User).filter(
            User.username == "user",
            User.tenant_id == demo_tenant.id
        ).first()
        
        if not regular_user:
            regular_user = User(
                username="user",
                email="user@demo.hse-system.com",
                password_hash=get_password_hash("User123!"),
                first_name="Demo",
                last_name="User",
                role="user",
                tenant_id=demo_tenant.id,
                department="Safety",
                is_active=True,
                is_verified=True
            )
            db.add(regular_user)
            db.commit()
            logger.info("Created user: user / User123!")
        else:
            # Update password to match expected credentials
            regular_user.password_hash = get_password_hash("User123!")
            db.commit()
            logger.info("Updated user password to: User123!")
        
        logger.info("Demo users created/updated successfully!")
        
    except Exception as e:
        logger.error(f"Error creating demo users: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_demo_users()
    print("\n=== Demo Users Initialized ===")
    print("\nDemo Tenant: demo.hse-system.com")
    print("\nCredentials:")
    print("  Admin: admin / Admin123!")
    print("  User: user / User123!")
    print("\nYou can now login with these credentials.")