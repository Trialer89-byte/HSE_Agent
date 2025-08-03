from typing import List, Dict, Set
from functools import wraps
from fastapi import HTTPException, status

from app.models.user import User


# Permission levels and their associated permissions
PERMISSION_LEVELS = {
    "super_admin": [
        "system.*",           # Full system access
        "tenant.*",          # All tenant management
        "user.*"             # All user management
    ],
    "admin": [
        "tenant.permits.*",   # All permits in tenant
        "tenant.documents.*", # All documents in tenant
        "tenant.users.read",  # Read tenant users
        "tenant.reports.*"    # All reports
    ],
    "manager": [
        "department.permits.*",      # Department permits
        "department.documents.read", # Read department docs
        "own.permits.*",            # Own permits
        "department.analysis.*"      # Department analysis
    ],
    "operator": [
        "own.permits.*",            # Own permits only
        "tenant.documents.read",    # Read company docs
        "own.analysis.read"         # Own analysis results
    ],
    "viewer": [
        "own.permits.read",         # Read own permits
        "tenant.documents.read"     # Read company docs
    ]
}


def get_user_permissions(role: str, custom_permissions: List[str] = None) -> Set[str]:
    """
    Get all permissions for a user based on role and custom permissions
    """
    permissions = set()
    
    # Add role-based permissions
    if role in PERMISSION_LEVELS:
        permissions.update(PERMISSION_LEVELS[role])
    
    # Add custom permissions
    if custom_permissions:
        permissions.update(custom_permissions)
    
    return permissions


def has_permission(user: User, required_permission: str) -> bool:
    """
    Check if user has required permission
    """
    user_permissions = get_user_permissions(user.role, user.permissions or [])
    
    # Check for global wildcard (super admin)
    if "*" in user_permissions:
        return True
    
    # Check exact match
    if required_permission in user_permissions:
        return True
    
    # Check wildcard permissions
    for perm in user_permissions:
        if perm.endswith(".*"):
            prefix = perm[:-2]
            if required_permission.startswith(prefix):
                return True
    
    return False


def require_permission(permission: str):
    """
    Decorator to require specific permission for endpoint access
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user from kwargs
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Check permission
            if not has_permission(current_user, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission '{permission}' required"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(required_role: str):
    """
    Decorator to require specific role for endpoint access
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            if current_user.role != required_role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role '{required_role}' required"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def check_tenant_access(user: User, resource_tenant_id: int) -> bool:
    """
    Check if user can access resource from specific tenant
    """
    # Super admin can access all tenants
    if user.role == "super_admin":
        return True
    
    # Users can only access their own tenant
    return user.tenant_id == resource_tenant_id


def filter_by_permission(user: User, base_query, resource_type: str):
    """
    Filter query based on user permissions
    """
    # Super admin sees everything
    if user.role == "super_admin":
        return base_query
    
    # Admin sees everything in tenant
    if user.role == "admin":
        return base_query.filter_by(tenant_id=user.tenant_id)
    
    # Manager sees department + own
    if user.role == "manager":
        return base_query.filter(
            (base_query.model.tenant_id == user.tenant_id) &
            ((base_query.model.created_by == user.id) | 
             (base_query.model.department == user.department))
        )
    
    # Operator/viewer sees only own
    return base_query.filter(
        (base_query.model.tenant_id == user.tenant_id) &
        (base_query.model.created_by == user.id)
    )