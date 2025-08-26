"""
Authentication and user schemas
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, validator
import uuid

from app.models.user import User

class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    phone: Optional[str] = None
    specialization: Optional[str] = None
    license_number: Optional[str] = None
    registration_number: Optional[str] = None

class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v

class UserRegister(UserBase):
    """User registration schema"""
    password: str
    confirm_password: str
    tenant_id: Optional[uuid.UUID] = None
    roles: List[str] = ["staff"]
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
    
    @validator('confirm_password')
    def validate_confirm_password(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not v.startswith('+91'):
            raise ValueError('Phone number must start with +91 for India')
        return v

class UserResponse(BaseModel):
    """User response schema"""
    id: uuid.UUID
    email: str
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    phone: Optional[str] = None
    roles: List[str]
    specialization: Optional[str] = None
    license_number: Optional[str] = None
    registration_number: Optional[str] = None
    is_active: bool
    is_verified: bool
    abha_id: Optional[str] = None
    hpr_id: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    country: str = "India"
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    mfa_enabled: bool = False
    preferences: dict = {}
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    @classmethod
    def from_user(cls, user: User) -> "UserResponse":
        """Create UserResponse from User model"""
        return cls(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            middle_name=user.middle_name,
            phone=user.phone,
            roles=user.roles,
            specialization=user.specialization,
            license_number=user.license_number,
            registration_number=user.registration_number,
            is_active=user.is_active,
            is_verified=user.is_verified,
            abha_id=user.abha_id,
            hpr_id=user.hpr_id,
            address=user.address,
            city=user.city,
            state=user.state,
            pincode=user.pincode,
            country=user.country,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login,
            mfa_enabled=user.mfa_enabled,
            preferences=user.preferences
        )
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: float
    user: UserResponse

class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str

class PasswordResetRequest(BaseModel):
    """Password reset request schema"""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema"""
    token: str
    new_password: str
    confirm_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
    
    @validator('confirm_password')
    def validate_confirm_password(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

class UserUpdate(BaseModel):
    """User update schema"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    phone: Optional[str] = None
    specialization: Optional[str] = None
    license_number: Optional[str] = None
    registration_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    preferences: Optional[dict] = None
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not v.startswith('+91'):
            raise ValueError('Phone number must start with +91 for India')
        return v

class MFAEnableRequest(BaseModel):
    """MFA enable request schema"""
    enable: bool

class MFAVerifyRequest(BaseModel):
    """MFA verification request schema"""
    code: str 