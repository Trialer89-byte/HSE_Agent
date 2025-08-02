from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Nome utente")
    email: EmailStr = Field(..., description="Email utente")
    first_name: Optional[str] = Field(None, max_length=100, description="Nome")
    last_name: Optional[str] = Field(None, max_length=100, description="Cognome")
    department: Optional[str] = Field(None, max_length=100, description="Dipartimento")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Password (minimo 8 caratteri)")
    role: str = Field(default="viewer", description="Ruolo utente")
    tenant_id: int = Field(..., description="ID del tenant")

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

    @validator('role')
    def validate_role(cls, v):
        allowed_roles = ['super_admin', 'admin', 'manager', 'operator', 'viewer']
        if v not in allowed_roles:
            raise ValueError(f'Role must be one of: {allowed_roles}')
        return v


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    role: Optional[str] = None
    permissions: Optional[List[str]] = None
    is_active: Optional[bool] = None

    @validator('role')
    def validate_role(cls, v):
        if v is not None:
            allowed_roles = ['super_admin', 'admin', 'manager', 'operator', 'viewer']
            if v not in allowed_roles:
                raise ValueError(f'Role must be one of: {allowed_roles}')
        return v


class UserResponse(UserBase):
    id: int
    tenant_id: int
    role: str
    permissions: List[str]
    is_active: bool
    is_verified: bool
    last_login: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str = Field(..., description="Nome utente o email")
    password: str = Field(..., description="Password")
    tenant_domain: Optional[str] = Field(None, description="Dominio tenant (opzionale)")


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class PasswordChangeRequest(BaseModel):
    current_password: str = Field(..., description="Password attuale")
    new_password: str = Field(..., min_length=8, description="Nuova password")

    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class TokenPayload(BaseModel):
    sub: str
    tenant_id: int
    exp: int
    iat: int
    type: str