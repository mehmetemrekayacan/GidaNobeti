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


class OrderUploadResponse(BaseModel):
    order_id: UUID
    restaurant_name: str | None
    restaurant_id: int | None
    total_amount: float | None
    raw_ocr_text: str
    ocr_confidence: float
    warnings: list[str] = Field(default_factory=list)
    receipt_date: datetime | None
