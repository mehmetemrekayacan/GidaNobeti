"""
Order API - Sipariş yükleme (TASK-BE-011) & Geçmiş (TASK-BE-012)
"""
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Query, Request
from app.core.limiter import limiter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.db.models.order import Order, OrderItem, EntryMethod
from app.db.models.restaurant import RiskStatus
from app.core.deps import get_current_user
from app.db.models.user import User
from app.services.ocr_service import ocr_service
from app.services.parser_service import parser_service
from app.services.restaurant_service import find_or_create_restaurant
from app.schemas.order import (
    OrderUploadResponse,
    OrderHistoryListResponse,
    OrderHistoryEntrySchema,
    OrderHistoryItemSchema,
    RestaurantSummarySchema,
)

router = APIRouter(prefix="/orders", tags=["Orders"])
logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/jpg"}


@router.get("/my-history", response_model=OrderHistoryListResponse)
async def get_my_order_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Sayfa numarası"),
    limit: int = Query(20, ge=1, le=100, description="Sayfa başına kayıt"),
    start_date: datetime | None = Query(None, description="Başlangıç tarihi (UTC)"),
    end_date: datetime | None = Query(None, description="Bitiş tarihi (UTC)"),
    restaurant_id: int | None = Query(None, description="Restoran ID filtresi"),
):
    """
    Kullanıcının sipariş geçmişini listeler. Sadece kendi siparişleri görünür.
    Sıralama: declared_at DESC (en yeni önce).
    """
    # Filtre koşulları
    conditions = [Order.user_id == current_user.id]
    if start_date:
        conditions.append(Order.declared_at >= start_date)
    if end_date:
        conditions.append(Order.declared_at <= end_date)
    if restaurant_id is not None:
        conditions.append(Order.restaurant_id == restaurant_id)

    # Toplam sayı
    count_stmt = select(func.count()).select_from(Order).where(and_(*conditions))
    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one() or 0

    # Sayfalı sorgu (restaurant + items eager load)
    offset = (page - 1) * limit
    stmt = (
        select(Order)
        .where(and_(*conditions))
        .order_by(Order.declared_at.desc())
        .offset(offset)
        .limit(limit)
    )
    stmt = stmt.options(
        selectinload(Order.restaurant),
        selectinload(Order.items),
    )
    result = await db.execute(stmt)
    orders = result.scalars().all()

    # Response oluştur
    items = []
    for order in orders:
        restaurant_schema = None
        if order.restaurant:
            restaurant_schema = RestaurantSummarySchema(
                id=order.restaurant.id,
                name=order.restaurant.name,
                current_risk_status=order.restaurant.current_risk_status.value,
            )
        item_schemas = [
            OrderHistoryItemSchema(
                item_name=oi.item_name,
                quantity=oi.quantity,
                unit_price=float(oi.unit_price) if oi.unit_price is not None else None,
            )
            for oi in order.items
        ]
        items.append(
            OrderHistoryEntrySchema(
                id=order.id,
                declared_at=order.declared_at,
                receipt_date=order.receipt_date,
                total_amount=float(order.total_amount) if order.total_amount is not None else None,
                method=order.method.value,
                restaurant=restaurant_schema,
                items=item_schemas,
            )
        )

    return OrderHistoryListResponse(
        total=total,
        page=page,
        limit=limit,
        items=items,
    )


@router.post("/upload", response_model=OrderUploadResponse)
@limiter.limit("10/hour")
async def upload_receipt(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Fiş fotoğrafı yükle, OCR ile işle, sipariş kaydet.
    KVKK: Görsel sunucuda saklanmaz.
    """
    # Validasyon
    if file.content_type and file.content_type.lower() not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sadece JPEG/PNG kabul edilir",
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Görsel 5MB'dan büyük olamaz",
        )

    warnings = []

    try:
        # OCR
        raw_text, confidence = ocr_service.extract(content)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception("OCR failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Fiş okunamadı, lütfen daha net bir fotoğraf deneyin",
        )
    finally:
        del content  # KVKK: RAM'den hemen sil

    if not raw_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fişten metin çıkarılamadı",
        )

    # Parse
    parsed = parser_service.parse(raw_text)

    # Restaurant find/create
    restaurant = None
    if parsed.restaurant_name:
        try:
            restaurant, _ = await find_or_create_restaurant(
                db, parsed.restaurant_name, "Bilinmiyor"
            )
            if restaurant.current_risk_status in (
                RiskStatus.RED_FLAG,
                RiskStatus.BLACKLISTED,
            ):
                warnings.append(
                    f"Dikkat: {restaurant.name} riskli restoran listesinde!"
                )
        except Exception as e:
            logger.warning("Restaurant find/create failed: %s", e)
            pass

    # receipt_date timezone-aware yap (naive ise)
    receipt_dt = None
    if parsed.receipt_date:
        receipt_dt = (
            parsed.receipt_date.replace(tzinfo=timezone.utc)
            if parsed.receipt_date.tzinfo is None
            else parsed.receipt_date
        )

    # Order oluştur
    order = Order(
        user_id=current_user.id,
        restaurant_id=restaurant.id if restaurant else None,
        method=EntryMethod.SCREENSHOT,
        raw_ocr_text=raw_text,
        ocr_confidence=confidence,
        total_amount=parsed.total_amount,
        receipt_date=receipt_dt,
    )
    db.add(order)
    await db.flush()

    # Order items (item_name max 255 karakter, unit_price NUMERIC(10,2) overflow önle)
    MAX_UNIT_PRICE = 99_999_999.99  # DB NUMERIC(10,2) üst sınır
    for item in parsed.items:
        item_name = (item["name"] or "")[:255]
        if not item_name:
            continue
        up = item.get("unit_price")
        if up is not None and up > MAX_UNIT_PRICE:
            up = None  # Overflow önle
        oi = OrderItem(
            order_id=order.id,
            item_name=item_name,
            quantity=item["quantity"],
            unit_price=up,
        )
        db.add(oi)

    # Restaurant total_orders güncelle
    if restaurant:
        restaurant.total_orders = (restaurant.total_orders or 0) + 1

    await db.commit()
    await db.refresh(order)

    return OrderUploadResponse(
        order_id=order.id,
        restaurant_name=restaurant.name if restaurant else parsed.restaurant_name,
        restaurant_id=restaurant.id if restaurant else None,
        total_amount=parsed.total_amount,
        raw_ocr_text=raw_text,
        ocr_confidence=confidence,
        warnings=warnings,
        receipt_date=receipt_dt,
    )
