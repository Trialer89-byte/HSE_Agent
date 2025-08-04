#!/usr/bin/env python3
"""Reset admin password to default"""

from sqlalchemy.orm import Session
from app.config.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def reset_admin_password():
    db = SessionLocal()
    try:
        # Find admin user
        admin_user = db.query(User).filter(
            User.username == "admin",
            User.tenant_id == 1
        ).first()
        
        if admin_user:
            # Reset password
            admin_user.password_hash = get_password_hash("HSEAdmin2024!")
            admin_user.failed_login_attempts = 0
            admin_user.is_active = True
            db.commit()
            print(f"✓ Reset password for admin user (ID: {admin_user.id})")
            print(f"  Username: admin")
            print(f"  Password: HSEAdmin2024!")
            print(f"  Email: {admin_user.email}")
        else:
            print("❌ Admin user not found")
            
    finally:
        db.close()

if __name__ == "__main__":
    reset_admin_password()