from typing import Optional
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.security import verify_password, get_password_hash, create_access_token, decode_token
from app.models.user import User
from app.models.tenant import Tenant
from app.config.database import get_db


security = HTTPBearer()


class AuthService:
    """
    Authentication service for user management
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def authenticate_user(self, username: str, password: str, tenant_id: int) -> Optional[User]:
        """
        Authenticate user with username/password
        """
        user = self.db.query(User).filter(
            User.username == username,
            User.tenant_id == tenant_id,
            User.is_active == True
        ).first()
        
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            # Increment failed login attempts
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.is_active = False  # Lock account after 5 failed attempts
            self.db.commit()
            return None
        
        # Reset failed attempts on successful login
        user.failed_login_attempts = 0
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        return user
    
    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        tenant_id: int,
        first_name: str = None,
        last_name: str = None,
        role: str = "viewer",
        department: str = None
    ) -> User:
        """
        Create new user
        """
        # Check if username already exists in tenant
        existing_user = self.db.query(User).filter(
            User.username == username,
            User.tenant_id == tenant_id
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists in this tenant"
            )
        
        # Check email uniqueness in tenant
        existing_email = self.db.query(User).filter(
            User.email == email,
            User.tenant_id == tenant_id
        ).first()
        
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists in this tenant"
            )
        
        # Create user
        user = User(
            username=username,
            email=email,
            password_hash=get_password_hash(password),
            tenant_id=tenant_id,
            first_name=first_name,
            last_name=last_name,
            role=role,
            department=department
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def get_user_by_id(self, user_id: int, tenant_id: int) -> Optional[User]:
        """
        Get user by ID with tenant validation
        """
        return self.db.query(User).filter(
            User.id == user_id,
            User.tenant_id == tenant_id,
            User.is_active == True
        ).first()
    
    def update_user_password(self, user: User, new_password: str) -> User:
        """
        Update user password
        """
        user.password_hash = get_password_hash(new_password)
        user.failed_login_attempts = 0  # Reset failed attempts
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def deactivate_user(self, user: User) -> User:
        """
        Deactivate user account
        """
        user.is_active = False
        self.db.commit()
        self.db.refresh(user)
        return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user
    """
    try:
        payload = decode_token(credentials.credentials)
        user_id = int(payload.get("sub"))
        tenant_id = int(payload.get("tenant_id"))
        
        if not user_id or not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        auth_service = AuthService(db)
        user = auth_service.get_user_by_id(user_id, tenant_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Verify tenant is active
        tenant = db.query(Tenant).filter(
            Tenant.id == tenant_id,
            Tenant.is_active == True
        ).first()
        
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant not found or inactive"
            )
        
        return user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )


async def get_current_super_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to require super admin role
    """
    if current_user.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    return current_user


async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to require admin role or higher
    """
    if current_user.role not in ["super_admin", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user