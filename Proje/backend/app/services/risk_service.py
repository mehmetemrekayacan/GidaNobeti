"""
Risk Analysis Service - Otomatik risk statüsü güncelleme (TASK-BE-014/015)
- Tek restoran: update_restaurant_risk_status (incident sonrası çağrılır)
- Tüm restoranlar: update_all_restaurants_risk_status (cron ile saatlik)
"""
import asyncio
import traceback
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.db.models.incident import HealthIncident
from app.db.models.order import Order
from app.db.models.restaurant import Restaurant, RiskStatus

# RED_FLAG olduğunda çağrılacak hook (bildirim vb. - ileride genişletilebilir)
def on_risk_red_flag(restaurant_id: int, restaurant_name: str | None) -> None:
    """RED_FLAG olduğunda tetiklenir; log + ileride push/email eklenebilir."""
    logger.warning(
        "Restoran risk RED_FLAG: id={} name={}",
        restaurant_id,
        restaurant_name or "?",
    )

# Son 24 saat
RECENT_HOURS = 24
RED_FLAG_THRESHOLD = 3  # Son 24 saatte 3+ şikayet → RED_FLAG
WATCHLIST_THRESHOLD = 2  # Son 24 saatte 2 şikayet → WATCHLIST
COMPLAINT_RATE_THRESHOLD = 0.05  # %5'ten fazla → WATCHLIST


async def update_restaurant_risk_status(db: AsyncSession, restaurant_id: int) -> None:
    """
    Restoran risk statüsünü otomatik günceller.
    Algoritma (SPEC):
    - Son 24 saatte 3+ şikayet → RED_FLAG
    - Son 24 saatte 2 şikayet → WATCHLIST
    - Şikayet oranı >5% → WATCHLIST
    - Aksi halde → SAFE (mevcut RED_FLAG/BLACKLISTED değiştirilmez - admin manuel)
    """
    now = datetime.now(timezone.utc)
    since = now - timedelta(hours=RECENT_HOURS)

    # Son 24 saatte bu restoran ile ilişkili incident sayısı
    recent_count_stmt = (
        select(func.count(HealthIncident.id))
        .join(Order, HealthIncident.suspected_order_id == Order.id)
        .where(
            and_(
                Order.restaurant_id == restaurant_id,
                HealthIncident.report_date >= since,
            )
        )
    )
    recent_result = await db.execute(recent_count_stmt)
    recent_incidents = recent_result.scalar_one() or 0

    # Restoran bilgisi
    rest_result = await db.execute(
        select(Restaurant).where(Restaurant.id == restaurant_id)
    )
    restaurant = rest_result.scalar_one_or_none()
    if not restaurant:
        return

    total_orders = restaurant.total_orders or 0
    total_complaints = restaurant.total_complaints or 0
    complaint_rate = total_complaints / max(total_orders, 1)
    current = restaurant.current_risk_status

    new_status = current
    reason = None

    if recent_incidents >= RED_FLAG_THRESHOLD:
        new_status = RiskStatus.RED_FLAG
        reason = f"Son {RECENT_HOURS} saatte {recent_incidents} şikayet alındı."
    elif recent_incidents >= WATCHLIST_THRESHOLD:
        new_status = RiskStatus.WATCHLIST
        reason = f"Son {RECENT_HOURS} saatte {recent_incidents} şikayet. İzleme altında."
    elif complaint_rate > COMPLAINT_RATE_THRESHOLD:
        new_status = RiskStatus.WATCHLIST
        reason = f"Şikayet oranı yüksek (%{complaint_rate * 100:.1f})"
    elif current == RiskStatus.SAFE or current == RiskStatus.WATCHLIST:
        # SAFE/WATCHLIST'dan düşüş: şikayet yoksa SAFE
        if recent_incidents == 0 and complaint_rate <= COMPLAINT_RATE_THRESHOLD:
            new_status = RiskStatus.SAFE
            reason = "Son dönemde şikayet yok."
    # RED_FLAG, BLACKLISTED → sadece admin manuel değiştirebilir, otomatik düşürme yok

    if new_status != current or reason:
        restaurant.current_risk_status = new_status
        restaurant.risk_updated_at = now
        restaurant.risk_reason = reason
        await db.flush()
        logger.info(
            "Restaurant {} risk updated: {} → {} ({})",
            restaurant_id, current.value, new_status.value, reason or "",
        )
        if new_status == RiskStatus.RED_FLAG and current != RiskStatus.RED_FLAG:
            on_risk_red_flag(restaurant_id, restaurant.name)


async def update_all_restaurants_risk_status(db: AsyncSession) -> int:
    """
    Tüm restoranların risk statüsünü günceller (cron job için).
    Dönüş: güncellenen restoran sayısı.
    """
    stmt = select(Restaurant.id).where(Restaurant.is_active == True)
    result = await db.execute(stmt)
    ids = [row[0] for row in result.all()]
    count = 0
    for rid in ids:
        try:
            await update_restaurant_risk_status(db, rid)
            count += 1
        except Exception as e:
            logger.error(
                "Risk update failed for restaurant {}. error_type={} error={} traceback={}",
                rid,
                type(e).__name__,
                str(e),
                traceback.format_exc(),
            )
    if ids:
        await db.commit()
    return count


async def run_risk_cron_loop() -> None:
    """Periyodik risk cron loop; hata olsa da döngü kırılmaz."""
    await asyncio.sleep(60)  # İlk çalışma 60 sn sonra (DB hazır olsun)
    while True:
        try:
            if settings.RISK_CRON_ENABLED:
                async with AsyncSessionLocal() as db:
                    n = await update_all_restaurants_risk_status(db)
                    if n > 0:
                        logger.info("Risk cron: {} restoran risk güncellendi", n)
        except asyncio.CancelledError:
            logger.info("Risk cron loop cancelled")
            break
        except Exception as e:
            logger.error(
                "Risk cron loop failed. interval={}s error_type={} error={} traceback={}",
                settings.RISK_CRON_INTERVAL_SECONDS,
                type(e).__name__,
                str(e),
                traceback.format_exc(),
            )

        await asyncio.sleep(settings.RISK_CRON_INTERVAL_SECONDS)
