"""
Restaurant Service - find_or_create (TASK-BE-010)
"""
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.restaurant import Restaurant, RiskStatus

logger = logging.getLogger(__name__)


def _normalize_for_match(name: str) -> str:
    """Eşleştirme için normalize (uppercase, trim)."""
    if not name:
        return ""
    return name.strip().upper()


async def find_or_create_restaurant(
    db: AsyncSession,
    name: str,
    platform_origin: str = "Bilinmiyor"
) -> tuple[Restaurant, bool]:
    """
    Restoran adına göre bul veya oluştur.

    Args:
        db: DB session
        name: OCR'dan gelen restoran adı
        platform_origin: Platform (Getir, Trendyol, vb.)

    Returns:
        (restaurant, created: bool)
    """
    if not name or not name.strip():
        raise ValueError("Restoran adı boş olamaz")

    normalized = _normalize_for_match(name)
    display_name = name.strip()

    # Önce tam eşleşme
    result = await db.execute(
        select(Restaurant).where(Restaurant.normalized_name == normalized)
    )
    existing = result.scalar_one_or_none()
    if existing:
        logger.debug(f"Restaurant found: {existing.name} (id={existing.id})")
        return existing, False

    # Yeni oluştur (ileride Levenshtein ile fuzzy matching eklenebilir)
    new_restaurant = Restaurant(
        name=display_name,
        normalized_name=normalized,
        platform_origin=platform_origin,
        current_risk_status=RiskStatus.SAFE,
        is_active=True,
    )
    db.add(new_restaurant)
    await db.commit()
    await db.refresh(new_restaurant)
    logger.info(f"Created new restaurant: {display_name} (id={new_restaurant.id})")
    return new_restaurant, True
