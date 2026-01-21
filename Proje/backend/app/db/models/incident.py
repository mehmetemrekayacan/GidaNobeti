"""
Health Incident Model - Sağlık Vakaları
"""
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import (
    Integer, String, Text, Boolean, DateTime, ForeignKey,
    Enum, Index, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from app.db.models.base import Base


class ReportStatus(str, PyEnum):
    """Health incident report status enumeration"""
    PENDING = "PENDING"
    INVESTIGATING = "INVESTIGATING"
    CONFIRMED = "CONFIRMED"
    DISMISSED = "DISMISSED"


class HealthIncident(Base):
    __tablename__ = "health_incidents"

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
    suspected_order_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="SET NULL")
    )
    
    # Incident Details
    symptoms: Mapped[str] = mapped_column(Text, nullable=False)
    symptom_start_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    severity_level: Mapped[int | None] = mapped_column(Integer)  # 1-5 scale
    
    # Doctor Verification
    is_verified_by_doctor: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    doctor_name: Mapped[str | None] = mapped_column(String(100))
    doctor_notes: Mapped[str | None] = mapped_column(Text)
    hospital_name: Mapped[str | None] = mapped_column(String(255))
    
    # Workflow
    report_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus, native_enum=False),
        default=ReportStatus.PENDING,
        nullable=False
    )
    admin_notes: Mapped[str | None] = mapped_column(Text)
    resolution_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    
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
    user: Mapped["User"] = relationship("User", back_populates="incidents")
    suspected_order: Mapped["Order"] = relationship("Order", back_populates="incidents")

    __table_args__ = (
        Index("idx_incidents_user", "user_id"),
        Index("idx_incidents_order", "suspected_order_id"),
        Index("idx_incidents_status", "status"),
        Index("idx_incidents_date", "report_date"),
        CheckConstraint(
            "severity_level BETWEEN 1 AND 5",
            name="chk_severity_range"
        ),
    )

    def __repr__(self) -> str:
        return f"<HealthIncident(id={self.id}, user_id={self.user_id}, status={self.status.value})>"
