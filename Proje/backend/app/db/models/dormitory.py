"""
Dormitory Model - Yurt Bilgileri
"""
from datetime import datetime
from sqlalchemy import (
    Integer, String, Text, Boolean, DateTime,
    Numeric, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.models.base import Base


class Dormitory(Base):
    __tablename__ = "dormitories"

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Basic Information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False, default="Isparta")
    district: Mapped[str | None] = mapped_column(String(100))
    address: Mapped[str | None] = mapped_column(Text)
    capacity: Mapped[int | None] = mapped_column(Integer)
    phone: Mapped[str | None] = mapped_column(String(20))
    
    # Location (for mapping)
    latitude: Mapped[float | None] = mapped_column(Numeric(10, 8))
    longitude: Mapped[float | None] = mapped_column(Numeric(11, 8))
    
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
    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="dormitory",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_dormitories_city", "city"),
        Index("idx_dormitories_active", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<Dormitory(id={self.id}, name='{self.name}', city='{self.city}')>"
