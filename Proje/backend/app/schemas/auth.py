"""
Authentication Schemas - Request/Response Models
"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from app.db.models.user import UserRole
import re


class RegisterRequest(BaseModel):
    """User registration request"""
    tckn: str = Field(..., min_length=11, max_length=11, description="TC Kimlik No")
    password: str = Field(..., min_length=8, max_length=72, description="Password (max 72 bytes)")
    full_name: str = Field(..., min_length=2, max_length=100, description="Full Name")
    email: str | None = Field(None, description="Email (optional)")
    phone: str | None = Field(None, max_length=20, description="Phone (optional)")
    dorm_id: int | None = Field(None, description="Dormitory ID")
    room_number: str | None = Field(None, max_length=20, description="Room Number")
    
    @field_validator('tckn')
    @classmethod
    def validate_tckn(cls, v: str) -> str:
        """Validate TCKN format"""
        # Remove whitespace
        v = v.strip().replace(' ', '')
        if not v.isdigit():
            raise ValueError("TCKN must contain only digits")
        if len(v) != 11:
            raise ValueError("TCKN must be exactly 11 digits")
        if v[0] == '0':
            raise ValueError("TCKN cannot start with 0")
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        # At least one letter and one number
        if not any(c.isalpha() for c in v):
            raise ValueError("Password must contain at least one letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class LoginRequest(BaseModel):
    """User login request"""
    tckn: str = Field(..., min_length=11, max_length=11, description="TC Kimlik No")
    password: str = Field(..., min_length=1, max_length=72, description="Password")
    
    @field_validator('tckn')
    @classmethod
    def validate_tckn(cls, v: str) -> str:
        """Validate TCKN format"""
        # Remove whitespace
        v = v.strip().replace(' ', '')
        if not v.isdigit():
            raise ValueError("TCKN must contain only digits")
        if len(v) != 11:
            raise ValueError("TCKN must be exactly 11 digits")
        if v[0] == '0':
            raise ValueError("TCKN cannot start with 0")
        return v


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Expiration time in seconds")
    user: "UserResponse"


class UserResponse(BaseModel):
    """User information response"""
    id: str  # UUID serialized as string
    tckn_hash: str
    full_name: str
    email: str | None
    phone_number: str | None
    room_number: str | None
    role: UserRole
    is_active: bool
    is_verified: bool
    dorm_id: int | None
    created_at: datetime
    
    @staticmethod
    def from_user(user) -> "UserResponse":
        """Convert User model to UserResponse"""
        return UserResponse(
            id=str(user.id),
            tckn_hash=user.tckn_hash,
            full_name=user.full_name,
            email=user.email,
            phone_number=user.phone_number,
            room_number=user.room_number,
            role=user.role,
            is_active=user.is_active,
            is_verified=user.is_verified,
            dorm_id=user.dorm_id,
            created_at=user.created_at
        )
    
    class Config:
        from_attributes = True
