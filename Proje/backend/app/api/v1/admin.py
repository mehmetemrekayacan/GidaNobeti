"""
Admin API Endpoints - Dashboard & Management (TASK-BE-007, TASK-AD-006)
"""
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
import json

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import from_url as redis_from_url

from app.core.config import settings
from app.db.session import get_db
from app.db.models.restaurant import Restaurant, RiskStatus
from app.db.models.order import Order
from app.db.models.user import User, UserRole
from app.db.models.incident import HealthIncident, ReportStatus
from app.core.deps import require_admin
from app.schemas.incident import (
    AdminIncidentListItem,
    AdminIncidentListResponse,
    AdminIncidentUpdateRequest,
)
from app.schemas.order import AdminOrderListItem, AdminOrderListResponse
from app.schemas.auth import AdminUserListItem, AdminUserListResponse

router = APIRouter(prefix="/admin", tags=["Admin"])

# Shared Redis client for lightweight caching (dashboard stats, etc.)
redis_client = redis_from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
)


@router.get("/dashboard/statistics")
async def get_dashboard_statistics(
    period: str = Query("last_7_days", description="Time period: last_7_days, last_30_days"),
    current_user: User = Depends(require_admin),
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
    cache_key = f"admin:dashboard:stats:{period}"

    # Try Redis cache when enabled (DASHBOARD_CACHE_ENABLED); skip in TESTING
    if settings.DASHBOARD_CACHE_ENABLED and not settings.TESTING:
        cached = await redis_client.get(cache_key)
        if cached:
            try:
                return json.loads(cached)
            except json.JSONDecodeError:
                # Corrupt cache; ignore and recompute
                pass

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
    
    # Daily breakdown (for charts): aggregate orders and incidents independently,
    # then merge by day so incident points are preserved even without same-day orders.
    daily_orders_query = (
        select(
            func.date(Order.declared_at).label("date"),
            func.count(Order.id).label("orders"),
        )
        .where(Order.declared_at >= start_date)
        .group_by(func.date(Order.declared_at))
        .order_by(func.date(Order.declared_at))
    )
    daily_incidents_query = (
        select(
            func.date(HealthIncident.report_date).label("date"),
            func.count(HealthIncident.id).label("incidents"),
        )
        .where(HealthIncident.report_date >= start_date)
        .group_by(func.date(HealthIncident.report_date))
        .order_by(func.date(HealthIncident.report_date))
    )

    daily_orders_result = await db.execute(daily_orders_query)
    daily_incidents_result = await db.execute(daily_incidents_query)

    daily_map: dict[str, dict[str, int]] = {}

    for date, orders in daily_orders_result.all():
        if not date:
            continue
        date_key = date.isoformat() if hasattr(date, "isoformat") else str(date)
        daily_map[date_key] = {
            "orders": orders or 0,
            "incidents": 0,
        }

    for date, incidents in daily_incidents_result.all():
        if not date:
            continue
        date_key = date.isoformat() if hasattr(date, "isoformat") else str(date)
        if date_key not in daily_map:
            daily_map[date_key] = {"orders": 0, "incidents": 0}
        daily_map[date_key]["incidents"] = incidents or 0

    daily_breakdown = [
        {
            "date": date_key,
            "orders": values["orders"],
            "incidents": values["incidents"],
        }
        for date_key, values in sorted(daily_map.items(), key=lambda item: item[0])
    ]

    response_payload = {
        "period": period,
        "total_orders": total_orders,
        "total_students": active_students,
        "total_incidents": total_incidents,
        "top_restaurants": top_restaurants,
        "incidents_by_restaurant": incidents_by_restaurant,
        "daily_breakdown": daily_breakdown,
    }

    # Store in Redis for 10 minutes (600s)
    if settings.DASHBOARD_CACHE_ENABLED and not settings.TESTING:
        try:
            await redis_client.set(cache_key, json.dumps(response_payload), ex=600)
        except Exception:
            # Cache failure should never break the endpoint
            pass

    return response_payload


@router.put("/restaurants/{restaurant_id}/risk-status")
async def update_restaurant_risk_status(
    restaurant_id: int,
    new_status: RiskStatus = Query(..., description="New risk status"),
    reason: Optional[str] = Query(None, description="Reason for status change"),
    current_user: User = Depends(require_admin),
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


# --- TASK-AD-006: Incidents Management ---

@router.get("/incidents", response_model=AdminIncidentListResponse)
async def list_incidents(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="PENDING, INVESTIGATING, CONFIRMED, DISMISSED"),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Sağlık vakalarını listele (Admin).
    """
    conditions = []
    if status:
        try:
            status_enum = ReportStatus(status)
            conditions.append(HealthIncident.status == status_enum)
        except ValueError:
            pass

    # Toplam sayı
    count_stmt = select(func.count(HealthIncident.id))
    if conditions:
        count_stmt = count_stmt.where(and_(*conditions))
    total = (await db.execute(count_stmt)).scalar() or 0

    # Sayfalı sorgu (user, order->restaurant eager load)
    offset = (page - 1) * limit
    stmt = select(HealthIncident)
    if conditions:
        stmt = stmt.where(and_(*conditions))
    stmt = (
        stmt.order_by(HealthIncident.report_date.desc())
        .offset(offset)
        .limit(limit)
    )
    stmt = stmt.options(
        selectinload(HealthIncident.user),
        selectinload(HealthIncident.suspected_order).selectinload(Order.restaurant),
    )
    result = await db.execute(stmt)
    incidents = result.scalars().all()

    items = []
    for hi in incidents:
        restaurant_name = None
        suspected_order_id = None
        if hi.suspected_order:
            suspected_order_id = hi.suspected_order.id
            if hi.suspected_order.restaurant:
                restaurant_name = hi.suspected_order.restaurant.name
        items.append(
            AdminIncidentListItem(
                id=hi.id,
                user_full_name=hi.user.full_name,
                restaurant_name=restaurant_name,
                suspected_order_id=suspected_order_id,
                symptoms=hi.symptoms[:200] + ("..." if len(hi.symptoms) > 200 else ""),
                severity_level=hi.severity_level,
                status=hi.status.value,
                report_date=hi.report_date,
                admin_notes=hi.admin_notes,
                is_verified_by_doctor=hi.is_verified_by_doctor,
                updated_at=hi.updated_at,
            )
        )

    return AdminIncidentListResponse(total=total, page=page, limit=limit, items=items)


# --- Admin Orders List ---


@router.get("/orders", response_model=AdminOrderListResponse)
async def list_admin_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Tüm siparişleri listele (Admin). Öğrenci adı, restoran, tarih, tutar, yöntem.
    """
    count_stmt = select(func.count(Order.id))
    total = (await db.execute(count_stmt)).scalar_one() or 0

    offset = (page - 1) * limit
    stmt = (
        select(Order)
        .order_by(Order.declared_at.desc())
        .offset(offset)
        .limit(limit)
    )
    stmt = stmt.options(
        selectinload(Order.user),
        selectinload(Order.restaurant),
    )
    result = await db.execute(stmt)
    orders = result.scalars().all()

    items = [
        AdminOrderListItem(
            id=o.id,
            student_name=o.user.full_name,
            restaurant_name=o.restaurant.name if o.restaurant else None,
            declared_at=o.declared_at,
            total_amount=float(o.total_amount) if o.total_amount is not None else None,
            food_content=o.food_content,
            method=o.method.value,
        )
        for o in orders
    ]

    return AdminOrderListResponse(total=total, page=page, limit=limit, items=items)


# --- Admin Users List (Öğrenci / kullanıcı listesi) ---


@router.get("/users", response_model=AdminUserListResponse)
async def list_admin_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    role: Optional[str] = Query(None, description="Filter by role: STUDENT, DORM_MANAGER, SECURITY, SYS_ADMIN"),
    search: Optional[str] = Query(None, description="Search by full name (case-insensitive)"),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Tüm kullanıcıları listele (Admin). Öğrenci listesi için role=STUDENT kullanın.
    TCKN ve şifre döndürülmez.
    """
    conditions = []
    if role:
        try:
            role_enum = UserRole(role)
            conditions.append(User.role == role_enum)
        except ValueError:
            pass
    if search and search.strip():
        pattern = f"%{search.strip()}%"
        conditions.append(User.full_name.ilike(pattern))

    count_stmt = select(func.count(User.id))
    if conditions:
        count_stmt = count_stmt.where(and_(*conditions))
    total = (await db.execute(count_stmt)).scalar_one() or 0

    offset = (page - 1) * limit
    stmt = (
        select(User)
        .options(selectinload(User.dormitory))
        .order_by(User.created_at.desc())
    )
    if conditions:
        stmt = stmt.where(and_(*conditions))
    stmt = stmt.offset(offset).limit(limit)
    result = await db.execute(stmt)
    users = result.scalars().all()

    items = [
        AdminUserListItem(
            id=str(u.id),
            full_name=u.full_name,
            email=u.email,
            phone_number=u.phone_number,
            room_number=u.room_number,
            role=u.role.value,
            is_active=u.is_active,
            is_verified=u.is_verified,
            dorm_name=u.dormitory.name if u.dormitory else None,
            created_at=u.created_at,
        )
        for u in users
    ]

    return AdminUserListResponse(total=total, page=page, limit=limit, items=items)


@router.put("/incidents/{incident_id}")
async def update_incident(
    incident_id: UUID,
    body: AdminIncidentUpdateRequest,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Vaka durumu ve admin notunu güncelle.
    """
    result = await db.execute(
        select(HealthIncident).where(HealthIncident.id == incident_id)
    )
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vaka bulunamadı",
        )

    if body.status is not None:
        try:
            incident.status = ReportStatus(body.status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Geçersiz durum: {body.status}",
            )
        if body.status in ("CONFIRMED", "DISMISSED"):
            incident.resolution_date = datetime.now()

    if body.admin_notes is not None:
        incident.admin_notes = body.admin_notes

    await db.commit()
    await db.refresh(incident)

    return {
        "success": True,
        "incident_id": str(incident.id),
        "status": incident.status.value,
        "message": "Vaka güncellendi",
    }
