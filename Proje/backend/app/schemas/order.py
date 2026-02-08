"""
Order Schemas - Sipariş API
"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class OrderItemResponse(BaseModel):
    item_name: str
    quantity: int
    unit_price: float | None


# --- Order History (TASK-BE-012) ---


class RestaurantSummarySchema(BaseModel):
    """Sipariş geçmişinde restoran özeti."""
    id: int
    name: str
    current_risk_status: str


class OrderHistoryItemSchema(BaseModel):
    """Sipariş geçmişinde ürün satırı."""
    item_name: str
    quantity: int
    unit_price: float | None


class OrderHistoryEntrySchema(BaseModel):
    """Tek bir sipariş geçmişi kaydı."""
    id: UUID
    declared_at: datetime
    receipt_date: datetime | None
    total_amount: float | None
    method: str
    restaurant: RestaurantSummarySchema | None
    items: list[OrderHistoryItemSchema] = Field(default_factory=list)


class OrderHistoryListResponse(BaseModel):
    """Sipariş geçmişi listesi (sayfalı)."""
    total: int
    page: int
    limit: int
    items: list[OrderHistoryEntrySchema]


class OrderUploadResponse(BaseModel):
    order_id: UUID
    restaurant_name: str | None
    restaurant_id: int | None
    total_amount: float | None
    raw_ocr_text: str
    ocr_confidence: float
    warnings: list[str] = Field(default_factory=list)
    receipt_date: datetime | None
