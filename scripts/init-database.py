#!/usr/bin/env python3
"""
Script di inizializzazione database per HSE Enterprise System

Crea tenant di default, utente super admin e documenti normativi base.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from sqlalchemy.orm import Session
from app.config.database import SessionLocal, engine, Base
from app.models import Tenant, User, Document
from app.services.auth_service import AuthService
from app.core.security import get_password_hash


def create_database_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")


def create_default_tenant(db: Session) -> Tenant:
    """Create default tenant"""
    print("Creating default tenant...")
    
    # Check if tenant already exists
    existing_tenant = db.query(Tenant).filter(Tenant.name == "Default Company").first()
    if existing_tenant:
        print("✓ Default tenant already exists")
        return existing_tenant
    
    tenant = Tenant(
        name="Default Company",
        domain="default.hse-enterprise.local",
        settings={
            "max_users": 100,
            "max_documents": 1000,
            "ai_analysis_enabled": True,
            "require_approval": True
        },
        subscription_plan="enterprise",
        max_users=100,
        max_documents=1000,
        is_active=True
    )
    
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    
    print(f"✓ Created default tenant: {tenant.name} (ID: {tenant.id})")
    return tenant


def create_super_admin(db: Session, tenant: Tenant) -> User:
    """Create super admin user"""
    print("Creating super admin user...")
    
    # Check if admin already exists
    existing_admin = db.query(User).filter(
        User.username == "admin",
        User.tenant_id == tenant.id
    ).first()
    
    if existing_admin:
        print("✓ Super admin already exists")
        return existing_admin
    
    admin_user = User(
        tenant_id=tenant.id,
        username="admin",
        email="admin@hse-enterprise.local",
        password_hash=get_password_hash("HSEAdmin2024!"),
        first_name="HSE",
        last_name="Administrator",
        role="super_admin",
        department="IT",
        is_active=True,
        is_verified=True
    )
    
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    print(f"✓ Created super admin: {admin_user.username}")
    print(f"  Login: admin / HSEAdmin2024!")
    return admin_user


def create_sample_users(db: Session, tenant: Tenant):
    """Create sample users with different roles"""
    print("Creating sample users...")
    
    sample_users = [
        {
            "username": "manager_eng",
            "email": "manager.eng@hse-enterprise.local",
            "password": "Manager123!",
            "first_name": "Mario",
            "last_name": "Rossi",
            "role": "manager",
            "department": "Engineering"
        },
        {
            "username": "operator_prod",
            "email": "operator.prod@hse-enterprise.local", 
            "password": "Operator123!",
            "first_name": "Luigi",
            "last_name": "Bianchi",
            "role": "operator",
            "department": "Production"
        },
        {
            "username": "viewer_maint",
            "email": "viewer.maint@hse-enterprise.local",
            "password": "Viewer123!",
            "first_name": "Giuseppe",
            "last_name": "Verdi",
            "role": "viewer",
            "department": "Maintenance"
        }
    ]
    
    created_count = 0
    for user_data in sample_users:
        # Check if user already exists
        existing_user = db.query(User).filter(
            User.username == user_data["username"],
            User.tenant_id == tenant.id
        ).first()
        
        if existing_user:
            continue
        
        user = User(
            tenant_id=tenant.id,
            username=user_data["username"],
            email=user_data["email"],
            password_hash=get_password_hash(user_data["password"]),
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            role=user_data["role"],
            department=user_data["department"],
            is_active=True,
            is_verified=True
        )
        
        db.add(user)
        created_count += 1
    
    db.commit()
    print(f"✓ Created {created_count} sample users")


def create_sample_documents(db: Session, tenant: Tenant, admin_user: User):
    """Create sample normative documents"""
    print("Creating sample documents...")
    
    sample_documents = [
        {
            "document_code": "D.Lgs 81/2008",
            "title": "Testo Unico sulla Salute e Sicurezza sul Lavoro",
            "document_type": "normativa",
            "category": "sicurezza",
            "authority": "Stato Italiano",
            "content_summary": "Decreto legislativo che disciplina la tutela della salute e della sicurezza nei luoghi di lavoro"
        },
        {
            "document_code": "UNI EN 397",
            "title": "Elmetti di protezione per l'industria",
            "document_type": "standard_tecnico",
            "category": "dpi",
            "authority": "UNI",
            "content_summary": "Standard tecnico per elmetti di protezione industriale"
        },
        {
            "document_code": "PROC_001",
            "title": "Procedura Generale Permessi di Lavoro",
            "document_type": "istruzione_operativa",
            "category": "procedura",
            "authority": "HSE Department",
            "content_summary": "Procedura aziendale per rilascio e gestione permessi di lavoro"
        },
        {
            "document_code": "PROC_002",
            "title": "Procedura Lavori in Spazi Confinati",
            "document_type": "istruzione_operativa",
            "category": "spazi_confinati",
            "authority": "HSE Department",
            "content_summary": "Procedura specifica per lavori in spazi confinati"
        }
    ]
    
    created_count = 0
    for doc_data in sample_documents:
        # Check if document already exists
        existing_doc = db.query(Document).filter(
            Document.document_code == doc_data["document_code"],
            Document.tenant_id == tenant.id
        ).first()
        
        if existing_doc:
            continue
        
        document = Document(
            tenant_id=tenant.id,
            document_code=doc_data["document_code"],
            title=doc_data["title"],
            document_type=doc_data["document_type"],
            category=doc_data["category"],
            authority=doc_data["authority"],
            content_summary=doc_data["content_summary"],
            scope="tenant",
            industry_sectors=["chimico", "manifatturiero", "edile"],
            uploaded_by=admin_user.id,
            is_active=True
        )
        
        db.add(document)
        created_count += 1
    
    db.commit()
    print(f"✓ Created {created_count} sample documents")


def print_summary():
    """Print initialization summary"""
    print("\n" + "="*60)
    print("🚀 HSE Enterprise System - Database Initialized!")
    print("="*60)
    print("\n📋 Default Credentials:")
    print("  Super Admin: admin / HSEAdmin2024!")
    print("  Manager:     manager_eng / Manager123!")
    print("  Operator:    operator_prod / Operator123!")
    print("  Viewer:      viewer_maint / Viewer123!")
    
    print("\n🏢 Default Tenant:")
    print("  Name: Default Company")
    print("  Domain: default.hse-enterprise.local")
    
    print("\n🌐 API Endpoints:")
    print("  Backend API: http://localhost:8000")
    print("  API Docs:    http://localhost:8000/api/docs")
    print("  Health:      http://localhost:8000/health")
    
    print("\n📚 Sample Data:")
    print("  - 4 normative/procedure documents")
    print("  - 4 users with different roles")
    print("  - Multi-tenant configuration")
    
    print("\n🔧 Next Steps:")
    print("  1. Start the application: docker-compose up -d")
    print("  2. Access API docs: http://localhost:8000/api/docs")
    print("  3. Login with admin credentials")
    print("  4. Create your first work permit")
    print("  5. Test AI analysis functionality")
    print("\n" + "="*60)


def main():
    """Main initialization function"""
    print("🚀 Initializing HSE Enterprise System Database...")
    print("="*60)
    
    try:
        # Create database tables
        create_database_tables()
        
        # Create session
        db = SessionLocal()
        
        try:
            # Create default tenant
            tenant = create_default_tenant(db)
            
            # Create super admin
            admin_user = create_super_admin(db, tenant)
            
            # Create sample users
            create_sample_users(db, tenant)
            
            # Create sample documents
            create_sample_documents(db, tenant, admin_user)
            
            print("\n✅ Database initialization completed successfully!")
            
        finally:
            db.close()
        
        # Print summary
        print_summary()
        
    except Exception as e:
        print(f"\n❌ Error during initialization: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()