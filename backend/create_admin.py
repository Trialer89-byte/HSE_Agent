from sqlalchemy.orm import Session
from app.config.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.tenant import Tenant
from app.core.security import get_password_hash

# Create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Create default tenant if not exists
tenant = db.query(Tenant).filter(Tenant.name == "Default Company").first()
if not tenant:
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
        is_active=True
    )
    db.add(tenant)
    db.commit()
    print("✓ Default tenant created")

# Create admin user if not exists
admin = db.query(User).filter(User.username == "admin").first()
if not admin:
    admin = User(
        username="admin",
        email="admin@hse-enterprise.local",
        password_hash=get_password_hash("HSEAdmin2024!"),
        first_name="System",
        last_name="Administrator",
        role="super_admin",
        permissions=["*"],
        is_active=True,
        is_verified=True,
        tenant_id=tenant.id
    )
    db.add(admin)
    db.commit()
    print("✓ Admin user created")
    print("  Username: admin")
    print("  Password: HSEAdmin2024!")
else:
    print("✓ Admin user already exists")

db.close()
print("\n✅ Database initialization complete!")