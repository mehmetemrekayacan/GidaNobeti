"""
User Model - Kullanıcı Bilgileri
"""
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import (
    Integer, String, Boolean, DateTime, ForeignKey,
    Enum, Index, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from app.db.models.base import Base


class UserRole(str, PyEnum):
    """User role enumeration"""
    STUDENT = "STUDENT"
    DORM_MANAGER = "DORM_MANAGER"
    SECURITY = "SECURITY"
    SYS_ADMIN = "SYS_ADMIN"


class User(Base):
    __tablename__ = "users"

    # Primary Key (UUID for security)
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Foreign Keys
    dorm_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("dormitories.id", ondelete="SET NULL")
    )
    
    # Identity (Encrypted)
    tckn_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True, default=None)
    phone_number: Mapped[str | None] = mapped_column(String(20))
    
    # Dorm Information
    room_number: Mapped[str | None] = mapped_column(String(20))
    
    # Authentication
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, native_enum=False),
        default=UserRole.STUDENT,
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Security & Activity
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    login_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    lockout_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    
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
    dormitory: Mapped["Dormitory"] = relationship("Dormitory", back_populates="users")
    orders: Mapped[list["Order"]] = relationship(
        "Order",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    incidents: Mapped[list["HealthIncident"]] = relationship(
        "HealthIncident",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_users_tckn_hash", "tckn_hash"),
        Index("idx_users_dorm", "dorm_id"),
        Index("idx_users_role", "role"),
        CheckConstraint(
            "email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'",
            name="chk_email_format"
        ),
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, name='{self.full_name}', role={self.role.value})>"
