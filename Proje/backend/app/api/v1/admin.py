"""
Admin API Endpoints - Dashboard & Management
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models.restaurant import Restaurant, RiskStatus
from app.db.models.order import Order
from app.db.models.user import User
from app.db.models.incident import HealthIncident

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard/statistics")
async def get_dashboard_statistics(
    period: str = Query("last_7_days", description="Time period: last_7_days, last_30_days"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get dashboard statistics for admin panel.
    
    Returns:
    - Total orders (in period)
    - Active students (who placed orders)
    - Total incidents
    - Top restaurants by order count
    - Incidents by restaurant
    - Daily breakdown for charts
    """
    # Calculate date range
    now = datetime.now()
    if period == "last_7_days":
        start_date = now - timedelta(days=7)
    elif period == "last_30_days":
        start_date = now - timedelta(days=30)
    else:
        start_date = now - timedelta(days=7)
    
    # Total orders in period
    orders_query = select(func.count(Order.id)).where(
        Order.declared_at >= start_date
    )
    total_orders = (await db.execute(orders_query)).scalar() or 0
    
    # Active students (distinct users who placed orders)
    active_students_query = select(func.count(func.distinct(Order.user_id))).where(
        Order.declared_at >= start_date
    )
    active_students = (await db.execute(active_students_query)).scalar() or 0
    
    # Total incidents
    incidents_query = select(func.count(HealthIncident.id)).where(
        HealthIncident.report_date >= start_date
    )
    total_incidents = (await db.execute(incidents_query)).scalar() or 0
    
    # Top 5 restaurants by order count
    top_restaurants_query = (
        select(
            Restaurant.name,
            func.count(Order.id).label("order_count")
        )
        .join(Order, Order.restaurant_id == Restaurant.id)
        .where(Order.declared_at >= start_date)
        .group_by(Restaurant.id, Restaurant.name)
        .order_by(func.count(Order.id).desc())
        .limit(5)
    )
    top_restaurants_result = await db.execute(top_restaurants_query)
    top_restaurants = [
        {"name": name, "order_count": count}
        for name, count in top_restaurants_result.all()
    ]
    
    # Incidents by restaurant
    incidents_by_restaurant_query = (
        select(
            Restaurant.name,
            func.count(HealthIncident.id).label("incident_count")
        )
        .join(Order, Order.restaurant_id == Restaurant.id)
        .join(HealthIncident, HealthIncident.suspected_order_id == Order.id)
        .where(HealthIncident.report_date >= start_date)
        .group_by(Restaurant.id, Restaurant.name)
        .order_by(func.count(HealthIncident.id).desc())
    )
    incidents_by_restaurant_result = await db.execute(incidents_by_restaurant_query)
    incidents_by_restaurant = [
        {"restaurant": name, "incident_count": count}
        for name, count in incidents_by_restaurant_result.all()
    ]
    
    # Daily breakdown (for charts)
    daily_breakdown_query = (
        select(
            func.date(Order.declared_at).label("date"),
            func.count(Order.id).label("orders"),
            func.count(func.distinct(HealthIncident.id)).label("incidents")
        )
        .outerjoin(
            HealthIncident,
            and_(
                HealthIncident.suspected_order_id == Order.id,
                func.date(HealthIncident.report_date) == func.date(Order.declared_at)
            )
        )
        .where(Order.declared_at >= start_date)
        .group_by(func.date(Order.declared_at))
        .order_by(func.date(Order.declared_at))
    )
    daily_breakdown_result = await db.execute(daily_breakdown_query)
    daily_breakdown = [
        {
            "date": date.isoformat() if date else None,
            "orders": orders or 0,
            "incidents": incidents or 0
        }
        for date, orders, incidents in daily_breakdown_result.all()
    ]
    
    return {
        "period": period,
        "total_orders": total_orders,
        "total_students": active_students,
        "total_incidents": total_incidents,
        "top_restaurants": top_restaurants,
        "incidents_by_restaurant": incidents_by_restaurant,
        "daily_breakdown": daily_breakdown
    }


@router.put("/restaurants/{restaurant_id}/risk-status")
async def update_restaurant_risk_status(
    restaurant_id: int,
    new_status: RiskStatus = Query(..., description="New risk status"),
    reason: Optional[str] = Query(None, description="Reason for status change"),
    db: AsyncSession = Depends(get_db)
):
    """
    Update restaurant risk status (Admin only).
    
    **Note:** In production, this should require DORM_MANAGER or SYS_ADMIN role.
    """
    # Get restaurant
    query = select(Restaurant).where(Restaurant.id == restaurant_id)
    result = await db.execute(query)
    restaurant = result.scalar_one_or_none()
    
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    
    # Update risk status
    restaurant.current_risk_status = new_status
    restaurant.risk_reason = reason
    restaurant.risk_updated_at = datetime.now()
    
    await db.commit()
    await db.refresh(restaurant)
    
    return {
        "success": True,
        "restaurant_id": restaurant_id,
        "new_status": new_status.value,
        "message": f"Restaurant risk status updated to {new_status.value}"
    }
