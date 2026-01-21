"""
Order Models - Sipariş & Sipariş Detayları
CRITICAL: NO image storage (KVKK compliance)
"""
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import (
    Integer, String, Text, Boolean, DateTime, ForeignKey,
    Numeric, Enum, Index, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from app.db.models.base import Base


class EntryMethod(str, PyEnum):
    """Order entry method enumeration"""
    SCREENSHOT = "SCREENSHOT"
    PHYSICAL_RECEIPT = "PHYSICAL_RECEIPT"
    MANUAL_ENTRY = "MANUAL_ENTRY"


class Order(Base):
    __tablename__ = "orders"

    # Primary Key (UUID)
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Foreign Keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    restaurant_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("restaurants.id", ondelete="SET NULL")
    )
    
    # Time Information
    declared_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    receipt_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    
    # Proof & Content (NO IMAGE STORAGE - KVKK Compliant)
    method: Mapped[EntryMethod] = mapped_column(
        Enum(EntryMethod, native_enum=False),
        nullable=False
    )
    raw_ocr_text: Mapped[str | None] = mapped_column(Text)  # OCR output only
    ocr_confidence: Mapped[float | None] = mapped_column(Numeric(5, 2))  # 0-100
    manual_note: Mapped[str | None] = mapped_column(Text)
    
    # Financial Information
    total_amount: Mapped[float | None] = mapped_column(Numeric(10, 2))
    
    # Security & Tracking
    client_ip: Mapped[str | None] = mapped_column(INET)
    user_agent: Mapped[str | None] = mapped_column(String(255))
    device_id: Mapped[str | None] = mapped_column(String(255))
    gps_latitude: Mapped[float | None] = mapped_column(Numeric(10, 8))
    gps_longitude: Mapped[float | None] = mapped_column(Numeric(11, 8))
    
    # Verification Status
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verification_notes: Mapped[str | None] = mapped_column(Text)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="orders")
    restaurant: Mapped["Restaurant"] = relationship("Restaurant", back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )
    incidents: Mapped[list["HealthIncident"]] = relationship(
        "HealthIncident",
        back_populates="suspected_order"
    )

    __table_args__ = (
        Index("idx_orders_user", "user_id"),
        Index("idx_orders_restaurant", "restaurant_id"),
        Index("idx_orders_date", "declared_at"),
        Index("idx_orders_receipt_date", "receipt_date"),
        Index("idx_orders_method", "method"),
    )

    def __repr__(self) -> str:
        return f"<Order(id={self.id}, user_id={self.user_id}, method={self.method.value})>"


class OrderItem(Base):
    __tablename__ = "order_items"

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Key
    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Item Details
    item_name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    unit_price: Mapped[float | None] = mapped_column(Numeric(10, 2))
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="items")

    __table_args__ = (
        Index("idx_order_items_order", "order_id"),
    )

    def __repr__(self) -> str:
        return f"<OrderItem(id={self.id}, name='{self.item_name}', qty={self.quantity})>"
