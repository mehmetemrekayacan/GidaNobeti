"""
Restaurant API Endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models.restaurant import Restaurant, RiskStatus
from app.schemas.restaurant import (
    RestaurantResponse,
    RestaurantListItem,
    RestaurantCreate,
    RestaurantUpdate
)

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])


@router.get("", response_model=list[RestaurantListItem])
async def list_restaurants(
    name: Optional[str] = Query(None, description="Search by restaurant name"),
    district: Optional[str] = Query(None, description="Filter by district"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    risk_status: Optional[RiskStatus] = Query(None, description="Filter by risk status"),
    is_active: bool = Query(True, description="Filter active restaurants"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of restaurants with optional filters
    
    - **name**: Search by restaurant name (case-insensitive)
    - **district**: Filter by district
    - **platform**: Filter by platform origin (Trendyol, Getir, etc.)
    - **risk_status**: Filter by risk status (SAFE, WATCHLIST, RED_FLAG, BLACKLISTED)
    - **is_active**: Show only active restaurants
    - **skip**: Pagination offset
    - **limit**: Max results per page
    """
    query = select(Restaurant)
    
    # Apply filters
    if name:
        search_pattern = f"%{name.upper()}%"
        query = query.where(
            or_(
                Restaurant.normalized_name.ilike(search_pattern),
                Restaurant.name.ilike(f"%{name}%")
            )
        )
    
    if district:
        query = query.where(Restaurant.district == district)
    
    if platform:
        query = query.where(Restaurant.platform_origin == platform)
    
    if risk_status:
        query = query.where(Restaurant.current_risk_status == risk_status)
    
    query = query.where(Restaurant.is_active == is_active)
    
    # Order by rating and total orders
    query = query.order_by(
        Restaurant.avg_rating.desc().nullslast(),
        Restaurant.total_orders.desc()
    )
    
    # Pagination
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    restaurants = result.scalars().all()
    
    return restaurants


@router.get("/{restaurant_id}", response_model=RestaurantResponse)
async def get_restaurant(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a specific restaurant
    
    - **restaurant_id**: Restaurant ID
    """
    query = select(Restaurant).where(Restaurant.id == restaurant_id)
    result = await db.execute(query)
    restaurant = result.scalar_one_or_none()
    
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    
    return restaurant


@router.get("/risky", response_model=list[RestaurantListItem])
async def get_risky_restaurants(
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of risky restaurants (WATCHLIST, RED_FLAG, BLACKLISTED).
    
    This endpoint is used by the mobile app home screen to display
    restaurants that students should avoid.
    
    Returns restaurants ordered by:
    1. Total complaints (descending)
    2. Risk status severity (RED_FLAG > WATCHLIST > BLACKLISTED)
    """
    query = select(Restaurant).where(
        Restaurant.current_risk_status.in_([
            RiskStatus.WATCHLIST,
            RiskStatus.RED_FLAG,
            RiskStatus.BLACKLISTED
        ])
    ).where(
        Restaurant.is_active == True
    ).order_by(
        Restaurant.total_complaints.desc(),
        Restaurant.current_risk_status.desc()
    )
    
    result = await db.execute(query)
    restaurants = result.scalars().all()
    
    return restaurants


@router.get("/stats/summary")
async def get_restaurant_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Get restaurant statistics summary
    
    Returns counts by risk status, active/inactive, and platform
    """
    # Total counts
    total_query = select(func.count(Restaurant.id))
    total_result = await db.execute(total_query)
    total = total_result.scalar()
    
    # Active count
    active_query = select(func.count(Restaurant.id)).where(Restaurant.is_active == True)
    active_result = await db.execute(active_query)
    active = active_result.scalar()
    
    # Risk status breakdown
    risk_query = select(
        Restaurant.current_risk_status,
        func.count(Restaurant.id)
    ).group_by(Restaurant.current_risk_status)
    risk_result = await db.execute(risk_query)
    risk_breakdown = {status: count for status, count in risk_result.all()}
    
    # Platform breakdown
    platform_query = select(
        Restaurant.platform_origin,
        func.count(Restaurant.id)
    ).where(Restaurant.platform_origin.isnot(None)).group_by(Restaurant.platform_origin)
    platform_result = await db.execute(platform_query)
    platform_breakdown = {platform: count for platform, count in platform_result.all()}
    
    return {
        "total_restaurants": total,
        "active_restaurants": active,
        "inactive_restaurants": total - active,
        "risk_status_breakdown": risk_breakdown,
        "platform_breakdown": platform_breakdown
    }


@router.post("", response_model=RestaurantResponse, status_code=status.HTTP_201_CREATED)
async def create_restaurant(
    restaurant: RestaurantCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new restaurant
    
    **Note:** This endpoint should be restricted to admin users in production
    """
    # Create normalized name for OCR matching
    normalized_name = restaurant.name.upper().strip()
    
    # Check if restaurant already exists
    existing_query = select(Restaurant).where(
        Restaurant.normalized_name == normalized_name
    )
    existing_result = await db.execute(existing_query)
    if existing_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Restaurant with this name already exists"
        )
    
    # Create restaurant
    db_restaurant = Restaurant(
        **restaurant.model_dump(),
        normalized_name=normalized_name
    )
    
    db.add(db_restaurant)
    await db.commit()
    await db.refresh(db_restaurant)
    
    return db_restaurant


@router.put("/{restaurant_id}", response_model=RestaurantResponse)
async def update_restaurant(
    restaurant_id: int,
    restaurant: RestaurantUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update restaurant information
    
    **Note:** This endpoint should be restricted to admin users in production
    """
    # Get existing restaurant
    query = select(Restaurant).where(Restaurant.id == restaurant_id)
    result = await db.execute(query)
    db_restaurant = result.scalar_one_or_none()
    
    if not db_restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    
    # Update fields
    update_data = restaurant.model_dump(exclude_unset=True)
    
    # Update normalized name if name changed
    if "name" in update_data:
        update_data["normalized_name"] = update_data["name"].upper().strip()
    
    for field, value in update_data.items():
        setattr(db_restaurant, field, value)
    
    await db.commit()
    await db.refresh(db_restaurant)
    
    return db_restaurant
