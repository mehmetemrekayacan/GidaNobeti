"""
Authentication Schemas - Request/Response Models
"""
from pydantic import BaseModel, Field, EmailStr, field_validator
from datetime import datetime
from app.db.models.user import UserRole
import re


class RegisterRequest(BaseModel):
    """User registration request"""
    tckn: str = Field(..., min_length=11, max_length=11, description="TC Kimlik No")
    password: str = Field(..., min_length=8, max_length=100, description="Password")
    full_name: str = Field(..., min_length=2, max_length=100, description="Full Name")
    email: EmailStr | None = Field(None, description="Email (optional)")
    phone: str | None = Field(None, max_length=20, description="Phone (optional)")
    dorm_id: int | None = Field(None, description="Dormitory ID")
    room_number: str | None = Field(None, max_length=20, description="Room Number")
    
    @field_validator('tckn')
    @classmethod
    def validate_tckn(cls, v: str) -> str:
        """Validate TCKN format"""
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
        if not re.search(r'[A-Z]', v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r'[a-z]', v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r'[0-9]', v):
            raise ValueError("Password must contain at least one digit")
        return v


class LoginRequest(BaseModel):
    """User login request"""
    tckn: str = Field(..., min_length=11, max_length=11, description="TC Kimlik No")
    password: str = Field(..., min_length=1, description="Password")


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Expiration time in seconds")
    user: "UserResponse"


class UserResponse(BaseModel):
    """User information response"""
    id: str
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
    
    class Config:
        from_attributes = True
