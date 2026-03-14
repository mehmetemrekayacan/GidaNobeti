"""Order API - parse/confirm flow and order history."""
import logging
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_current_user
from app.core.limiter import limiter
from app.db.models.order import EntryMethod, Order, OrderItem
from app.db.models.restaurant import Restaurant, RiskStatus
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.order import (
    OrderConfirmRequest,
    OrderConfirmResponse,
    OrderHistoryEntrySchema,
    OrderHistoryItemSchema,
    OrderHistoryListResponse,
    OrderParseResponse,
    ParsedOrderItemSchema,
    RestaurantSummarySchema,
)
from app.services.exceptions import ReceiptProcessingError
from app.services.ocr_service import ocr_service
from app.services.parser_service import parser_service
from app.services.restaurant_service import find_or_create_restaurant

router = APIRouter(prefix="/orders", tags=["Orders"])
logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_FILES = 2  # Trendyol gibi uzun fişler için max 2 görsel
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}


def _normalize_restaurant_name(name: str) -> str:
    return name.strip().upper()


def _build_parsed_item_schemas(items: list[dict]) -> list[ParsedOrderItemSchema]:
    parsed_items: list[ParsedOrderItemSchema] = []
    for item in items:
        item_name = (item.get("name") or "").strip()
        if not item_name:
            continue
        parsed_items.append(
            ParsedOrderItemSchema(
                item_name=item_name[:255],
                quantity=max(1, int(item.get("quantity") or 1)),
                unit_price=item.get("unit_price"),
            )
        )
    return parsed_items


def _dedupe_warnings(*warning_groups: list[str]) -> list[str]:
    deduped: list[str] = []
    seen: set[str] = set()
    for group in warning_groups:
        for warning in group:
            normalized = warning.strip()
            if not normalized or normalized in seen:
                continue
            deduped.append(normalized)
            seen.add(normalized)
    return deduped


def _restaurant_warnings(restaurant: Restaurant | None) -> list[str]:
    if restaurant is None:
        return []

    if restaurant.current_risk_status in (RiskStatus.RED_FLAG, RiskStatus.BLACKLISTED):
        return [f"Dikkat: {restaurant.name} riskli restoran listesinde!"]

    return []


def _ensure_aware_datetime(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value


async def _find_restaurant_preview(
    db: AsyncSession,
    restaurant_name: str | None,
) -> Restaurant | None:
    if not restaurant_name or not restaurant_name.strip():
        return None

    result = await db.execute(
        select(Restaurant).where(
            Restaurant.normalized_name == _normalize_restaurant_name(restaurant_name)
        )
    )
    return result.scalar_one_or_none()


async def _parse_receipt_files(files: List[UploadFile]):
    if len(files) > MAX_FILES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"En fazla {MAX_FILES} görsel yüklenebilir",
        )

    ocr_texts: list[str] = []
    total_confidence = 0.0

    for file in files:
        content_type = (file.content_type or "").lower()
        if content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Sadece resim formatları desteklenmektedir",
            )

        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Görsel 5MB'dan büyük olamaz",
            )

        try:
            text, confidence = ocr_service.extract(content)
            ocr_texts.append(text)
            total_confidence += confidence
        except ReceiptProcessingError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"detail": exc.detail, "error_code": exc.error_code},
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"detail": str(exc), "error_code": "OCR_UNREADABLE"},
            )
        except Exception:
            logger.exception("OCR failed")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "detail": "Fiş okunamadı veya restoran tespit edilemedi, lütfen daha net bir görüntü yükleyin",
                    "error_code": "OCR_UNREADABLE",
                },
            )
        finally:
            del content

    raw_text = "\n---\n".join(ocr_texts)
    confidence = total_confidence / len(files) if files else 0.0

    if not raw_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "detail": "Fiş okunamadı veya restoran tespit edilemedi, lütfen daha net bir görüntü yükleyin",
                "error_code": "OCR_UNREADABLE",
            },
        )

    try:
        parsed = parser_service.parse(raw_text)
    except ReceiptProcessingError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"detail": exc.detail, "error_code": exc.error_code},
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"detail": str(exc), "error_code": "PARSER_UNREADABLE"},
        )
    except Exception:
        logger.exception("Receipt parsing failed")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "detail": "Fiş okunamadı veya restoran tespit edilemedi, lütfen daha net bir görüntü yükleyin",
                "error_code": "PARSER_UNREADABLE",
            },
        )

    return parsed, raw_text, confidence


async def _build_parse_response(
    db: AsyncSession,
    parsed,
    raw_text: str,
    confidence: float,
) -> OrderParseResponse:
    restaurant = await _find_restaurant_preview(db, parsed.restaurant_name)
    warnings = _restaurant_warnings(restaurant)
    parsed_items = _build_parsed_item_schemas(parsed.items)

    return OrderParseResponse(
        restaurant_name=restaurant.name if restaurant else parsed.restaurant_name,
        restaurant_id=restaurant.id if restaurant else None,
        total_amount=parsed.total_amount,
        food_content=parsed.food_content,
        raw_ocr_text=raw_text,
        ocr_confidence=confidence,
        warnings=warnings,
        receipt_date=_ensure_aware_datetime(parsed.receipt_date),
        items=parsed_items,
    )


async def _create_order_from_confirmation(
    db: AsyncSession,
    current_user: User,
    request: Request,
    payload: OrderConfirmRequest,
) -> OrderConfirmResponse:
    restaurant_name = payload.restaurant_name.strip()
    if not restaurant_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Restoran adı boş olamaz",
        )

    restaurant, _ = await find_or_create_restaurant(db, restaurant_name, "Bilinmiyor")
    warnings = _dedupe_warnings(payload.warnings, _restaurant_warnings(restaurant))
    receipt_dt = _ensure_aware_datetime(payload.receipt_date)

    client_host = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    order = Order(
        user_id=current_user.id,
        restaurant_id=restaurant.id,
        method=EntryMethod.SCREENSHOT,
        raw_ocr_text=payload.raw_ocr_text,
        ocr_confidence=payload.ocr_confidence,
        total_amount=payload.total_amount,
        food_content=payload.food_content,
        receipt_date=receipt_dt,
        client_ip=client_host,
        user_agent=user_agent[:255] if user_agent else None,
    )
    db.add(order)
    await db.flush()

    max_unit_price = 99_999_999.99
    confirmed_items: list[ParsedOrderItemSchema] = []
    for item in payload.items:
        item_name = item.item_name.strip()[:255]
        if not item_name:
            continue

        unit_price = item.unit_price
        if unit_price is not None and unit_price > max_unit_price:
            unit_price = None

        db.add(
            OrderItem(
                order_id=order.id,
                item_name=item_name,
                quantity=max(1, item.quantity),
                unit_price=unit_price,
            )
        )
        confirmed_items.append(
            ParsedOrderItemSchema(
                item_name=item_name,
                quantity=max(1, item.quantity),
                unit_price=unit_price,
            )
        )

    restaurant.total_orders = (restaurant.total_orders or 0) + 1

    await db.commit()
    await db.refresh(order)

    return OrderConfirmResponse(
        order_id=order.id,
        restaurant_name=restaurant.name,
        restaurant_id=restaurant.id,
        total_amount=payload.total_amount,
        food_content=payload.food_content,
        raw_ocr_text=payload.raw_ocr_text,
        ocr_confidence=payload.ocr_confidence,
        warnings=warnings,
        receipt_date=receipt_dt,
        items=confirmed_items,
    )


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
                food_content=order.food_content,
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


@router.post("/parse", response_model=OrderParseResponse)
@limiter.limit("5/minute")
async def parse_receipt(
    request: Request,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Fiş fotoğrafını parse eder, fakat siparişi henüz kaydetmez.
    Mobil istemci bu sonucu kullanıcıya onaylatıp ardından /confirm çağırır.
    """
    del current_user
    parsed, raw_text, confidence = await _parse_receipt_files(files)
    return await _build_parse_response(db, parsed, raw_text, confidence)


@router.post("/upload", response_model=OrderParseResponse, deprecated=True)
@limiter.limit("5/minute")
async def upload_receipt(
    request: Request,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Backward compatible alias for parse-only upload flow."""
    return await parse_receipt(
        request=request,
        files=files,
        current_user=current_user,
        db=db,
    )


@router.post("/confirm", response_model=OrderConfirmResponse)
@limiter.limit("10/minute")
async def confirm_order(
    request: Request,
    payload: OrderConfirmRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Kullanıcının onayladığı sipariş bilgisini veritabanına kaydeder."""
    return await _create_order_from_confirmation(db, current_user, request, payload)
