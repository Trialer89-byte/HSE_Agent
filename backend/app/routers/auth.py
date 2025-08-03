from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from app.config.database import get_db
from app.config.settings import settings
from app.models.user import User
from app.models.tenant import Tenant
from app.schemas.auth import (
    LoginRequest, LoginResponse, UserCreate, UserResponse, 
    PasswordChangeRequest, UserUpdate
)
from app.services.auth_service import AuthService, get_current_user
from app.core.security import create_access_token
from app.core.tenant import get_tenant_from_domain
from app.core.audit import AuditService, get_client_ip, get_user_agent
from app.core.permissions import require_permission


router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])
security = HTTPBearer()


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Autentica l'utente e restituisce JWT token
    """
    # Determine tenant
    tenant = None
    if login_data.tenant_domain:
        tenant = get_tenant_from_domain(login_data.tenant_domain, db)
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
    else:
        # If no domain specified, try to find user across tenants
        # This is less secure but more user-friendly
        user_query = db.query(User).filter(
            User.username == login_data.username,
            User.is_active == True
        ).first()
        
        if user_query:
            tenant = db.query(Tenant).filter(
                Tenant.id == user_query.tenant_id,
                Tenant.is_active == True
            ).first()
    
    if not tenant:
        # Generic error for security
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Authenticate user
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(
        username=login_data.username,
        password=login_data.password,
        tenant_id=tenant.id
    )
    
    if not user:
        # Log failed login attempt
        audit_service = AuditService(db)
        await audit_service.log_authentication(
            tenant_id=tenant.id,
            username=login_data.username,
            success=False,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            failure_reason="Invalid username or password"
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Check if account is locked
    if not user.is_active:
        # Log locked account attempt
        audit_service = AuditService(db)
        await audit_service.log_authentication(
            tenant_id=tenant.id,
            username=login_data.username,
            success=False,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            failure_reason="Account is locked"
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is locked. Contact administrator."
        )
    
    # Create access token
    access_token = create_access_token(
        subject=str(user.id),
        tenant_id=tenant.id,
        expires_delta=timedelta(hours=settings.jwt_expiration_hours)
    )
    
    # Log successful login
    audit_service = AuditService(db)
    await audit_service.log_authentication(
        tenant_id=tenant.id,
        username=user.username,
        success=True,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.jwt_expiration_hours * 3600,
        user=UserResponse.from_orm(user)
    )


@router.post("/register", response_model=UserResponse)
@require_permission("tenant.users.create")
async def register_user(
    user_data: UserCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Registra un nuovo utente (richiede permessi admin)
    """
    # Verify tenant exists and user has permission
    tenant = db.query(Tenant).filter(
        Tenant.id == user_data.tenant_id,
        Tenant.is_active == True
    ).first()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    # Check if current user can create users in this tenant
    if current_user.role != "super_admin" and current_user.tenant_id != user_data.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create users in different tenant"
        )
    
    # Create user
    auth_service = AuthService(db)
    try:
        new_user = auth_service.create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            tenant_id=user_data.tenant_id,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role=user_data.role,
            department=user_data.department
        )
        
        # Audit log
        audit_service = AuditService(db)
        await audit_service.log_action(
            user_id=current_user.id,
            tenant_id=current_user.tenant_id,
            action="user.created",
            resource_type="user",
            resource_id=new_user.id,
            resource_name=new_user.username,
            new_values={
                "username": new_user.username,
                "email": new_user.email,
                "role": new_user.role,
                "tenant_id": new_user.tenant_id
            },
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            api_endpoint=request.url.path
        )
        
        return UserResponse.from_orm(new_user)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Ottieni informazioni dell'utente corrente
    """
    return UserResponse.from_orm(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Aggiorna informazioni dell'utente corrente
    """
    # Store old values for audit
    old_values = {
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "department": current_user.department
    }
    
    # Update user fields (excluding role and permissions for security)
    update_data = user_update.dict(exclude_unset=True, exclude={"role", "permissions", "is_active"})
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    # Audit log
    audit_service = AuditService(db)
    await audit_service.log_action(
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        action="user.updated_self",
        resource_type="user",
        resource_id=current_user.id,
        resource_name=current_user.username,
        old_values=old_values,
        new_values=update_data,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        api_endpoint=request.url.path
    )
    
    return UserResponse.from_orm(current_user)


@router.post("/change-password")
async def change_password(
    password_change: PasswordChangeRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cambia password dell'utente corrente
    """
    auth_service = AuthService(db)
    
    # Verify current password
    from app.core.security import verify_password
    if not verify_password(password_change.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    auth_service.update_user_password(current_user, password_change.new_password)
    
    # Audit log
    audit_service = AuditService(db)
    await audit_service.log_action(
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        action="user.password_changed",
        resource_type="user",
        resource_id=current_user.id,
        resource_name=current_user.username,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        api_endpoint=request.url.path,
        category="security"
    )
    
    return {"message": "Password changed successfully"}


@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout dell'utente (principalmente per audit)
    """
    # Log logout
    audit_service = AuditService(db)
    await audit_service.log_action(
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        action="auth.logout",
        resource_type="authentication",
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        api_endpoint=request.url.path,
        category="authentication"
    )
    
    return {"message": "Logged out successfully"}


@router.get("/users", response_model=List[UserResponse])
@require_permission("tenant.users.read")
async def list_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista utenti del tenant (richiede permessi admin)
    """
    # Super admin can see all users, others only their tenant
    if current_user.role == "super_admin":
        users = db.query(User).filter(User.is_active == True).all()
    else:
        users = db.query(User).filter(
            User.tenant_id == current_user.tenant_id,
            User.is_active == True
        ).all()
    
    return [UserResponse.from_orm(user) for user in users]


@router.put("/users/{user_id}", response_model=UserResponse)
@require_permission("tenant.users.update")
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Aggiorna un utente (richiede permessi admin)
    """
    # Find user to update
    user_to_update = db.query(User).filter(
        User.id == user_id,
        User.is_active == True
    ).first()
    
    if not user_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check permission to update this user
    if current_user.role != "super_admin" and user_to_update.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update users from different tenant"
        )
    
    # Store old values for audit
    old_values = {
        "email": user_to_update.email,
        "first_name": user_to_update.first_name,
        "last_name": user_to_update.last_name,
        "role": user_to_update.role,
        "department": user_to_update.department,
        "is_active": user_to_update.is_active
    }
    
    # Update user
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user_to_update, field, value)
    
    db.commit()
    db.refresh(user_to_update)
    
    # Audit log
    audit_service = AuditService(db)
    await audit_service.log_action(
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        action="user.updated",
        resource_type="user",
        resource_id=user_to_update.id,
        resource_name=user_to_update.username,
        old_values=old_values,
        new_values=update_data,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        api_endpoint=request.url.path
    )
    
    return UserResponse.from_orm(user_to_update)