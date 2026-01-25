"""
Restaurant Schemas - API Request/Response Models
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.db.models.restaurant import RiskStatus


class RestaurantBase(BaseModel):
    """Base restaurant schema"""
    name: str = Field(..., min_length=1, max_length=255)
    district: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = None
    platform_origin: Optional[str] = Field(None, max_length=50)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)


class RestaurantCreate(RestaurantBase):
    """Schema for creating a restaurant"""
    pass


class RestaurantUpdate(BaseModel):
    """Schema for updating a restaurant"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    district: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = None
    platform_origin: Optional[str] = Field(None, max_length=50)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    is_active: Optional[bool] = None
    current_risk_status: Optional[RiskStatus] = None
    risk_reason: Optional[str] = None


class RestaurantResponse(RestaurantBase):
    """Schema for restaurant response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    normalized_name: Optional[str]
    current_risk_status: RiskStatus
    risk_updated_at: Optional[datetime]
    risk_reason: Optional[str]
    total_complaints: int
    total_orders: int
    avg_rating: Optional[float]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class RestaurantListItem(BaseModel):
    """Lightweight schema for restaurant list"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    district: Optional[str]
    platform_origin: Optional[str]
    current_risk_status: RiskStatus
    avg_rating: Optional[float]
    total_orders: int
    total_complaints: int = 0
    is_active: bool


class RestaurantSearchParams(BaseModel):
    """Search/filter parameters"""
    name: Optional[str] = Field(None, description="Search by restaurant name")
    district: Optional[str] = Field(None, description="Filter by district")
    platform: Optional[str] = Field(None, description="Filter by platform origin")
    risk_status: Optional[RiskStatus] = Field(None, description="Filter by risk status")
    is_active: Optional[bool] = Field(True, description="Filter active restaurants")
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=100, description="Max records to return")
