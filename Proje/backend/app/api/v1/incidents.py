"""
Incidents API - Sağlık Vakası Bildirimi (TASK-BE-015)
"""
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.db.models.order import Order
from app.db.models.restaurant import Restaurant
from app.db.models.incident import HealthIncident
from app.core.deps import get_current_user
from app.db.models.user import User
from app.schemas.incident import IncidentReportRequest, IncidentReportResponse
from app.services.risk_service import update_restaurant_risk_status

router = APIRouter(prefix="/incidents", tags=["Incidents"])
logger = logging.getLogger(__name__)


@router.post("/report", response_model=IncidentReportResponse)
async def report_health_incident(
    body: IncidentReportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Sağlık sorunu bildirimi. Sadece kendi siparişin için şikayet edilebilir.
    """
    # Sipariş var mı ve kullanıcıya ait mi?
    order_result = await db.execute(
        select(Order).where(Order.id == body.suspected_order_id)
    )
    order = order_result.scalar_one_or_none()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sipariş bulunamadı",
        )
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Başka bir öğrencinin siparişi için şikayet edilemez",
        )

    # HealthIncident oluştur
    incident = HealthIncident(
        user_id=current_user.id,
        suspected_order_id=body.suspected_order_id,
        symptoms=body.symptoms,
        severity_level=body.severity_level,
    )
    db.add(incident)
    await db.flush()

    # Restaurant total_complaints artır
    if order.restaurant_id:
        rest_result = await db.execute(
            select(Restaurant).where(Restaurant.id == order.restaurant_id)
        )
        restaurant = rest_result.scalar_one_or_none()
        if restaurant:
            restaurant.total_complaints = (restaurant.total_complaints or 0) + 1
            await db.flush()
            await update_restaurant_risk_status(db, order.restaurant_id)

    await db.commit()
    await db.refresh(incident)

    next_steps = [
        "Bildiriminiz alındı."
    ]
    if body.severity_level >= 4:
        next_steps.append(
            "Ciddiyet seviyeniz yüksek. Yurt sağlık birimini veya acil servisi arayın."
        )
    next_steps.append("Yurt müdürü tarafından incelenecektir.")

    return IncidentReportResponse(
        incident_id=incident.id,
        next_steps=next_steps,
    )
