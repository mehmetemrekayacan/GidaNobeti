"""
Restaurant Model - Restoran & Risk Yönetimi
"""
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import (
    Integer, String, Text, Boolean, DateTime,
    Numeric, Enum, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.models.base import Base


class RiskStatus(str, PyEnum):
    """Restaurant risk status enumeration"""
    SAFE = "SAFE"
    WATCHLIST = "WATCHLIST"
    RED_FLAG = "RED_FLAG"
    BLACKLISTED = "BLACKLISTED"


class Restaurant(Base):
    __tablename__ = "restaurants"

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Basic Information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_name: Mapped[str | None] = mapped_column(String(255))  # UPPERCASE for OCR matching
    district: Mapped[str | None] = mapped_column(String(100))
    address: Mapped[str | None] = mapped_column(Text)
    
    # Platform Origin
    platform_origin: Mapped[str | None] = mapped_column(String(50))  # Trendyol, Getir, etc.
    
    # Risk Management
    current_risk_status: Mapped[RiskStatus] = mapped_column(
        Enum(RiskStatus, native_enum=False),
        default=RiskStatus.SAFE,
        nullable=False
    )
    risk_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    risk_reason: Mapped[str | None] = mapped_column(Text)
    total_complaints: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_orders: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Location
    latitude: Mapped[float | None] = mapped_column(Numeric(10, 8))
    longitude: Mapped[float | None] = mapped_column(Numeric(11, 8))
    
    # Statistics
    avg_rating: Mapped[float | None] = mapped_column(Numeric(3, 2))
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    orders: Mapped[list["Order"]] = relationship(
        "Order",
        back_populates="restaurant"
    )

    __table_args__ = (
        Index("idx_restaurants_name", "normalized_name"),
        Index("idx_restaurants_risk", "current_risk_status"),
        Index("idx_restaurants_platform", "platform_origin"),
    )

    def __repr__(self) -> str:
        return f"<Restaurant(id={self.id}, name='{self.name}', risk={self.current_risk_status.value})>"
