"""
Incident Schemas - Sağlık Vakası API (TASK-BE-015, TASK-AD-006)
"""
from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, Field


class IncidentCreate(BaseModel):
    """Sağlık vakası oluşturma isteği."""
    suspected_order_id: UUID = Field(..., description="Şüpheli sipariş ID")
    symptoms: str = Field(..., min_length=10, max_length=2000, description="Belirtiler")
    severity_level: int = Field(..., ge=1, le=5, description="Ciddiyet (1-5)")
    is_verified_by_doctor: Optional[bool] = Field(False, description="Doktor tarafından doğrulandı mı")


class IncidentReportRequest(IncidentCreate):
    """Sağlık vakası bildirimi isteği."""


class IncidentReportResponse(BaseModel):
    """Sağlık vakası bildirimi yanıtı."""
    incident_id: UUID
    next_steps: list[str] = Field(default_factory=list)


class MyIncidentListItem(BaseModel):
    """Öğrencinin kendi vaka listesi tek satır (Bildirimlerim)."""
    id: UUID
    restaurant_name: Optional[str] = None
    symptoms: str
    severity_level: Optional[int] = None
    status: str
    report_date: datetime


class MyIncidentListResponse(BaseModel):
    """Öğrencinin kendi vaka listesi yanıtı."""
    total: int
    page: int
    limit: int
    items: list[MyIncidentListItem]


# Admin schemas (TASK-AD-006)
class AdminIncidentListItem(BaseModel):
    """Admin incident listesi tek satır."""
    id: UUID
    user_full_name: str
    restaurant_name: Optional[str] = None
    suspected_order_id: Optional[UUID] = None
    symptoms: str
    severity_level: Optional[int] = None
    status: str
    report_date: datetime
    admin_notes: Optional[str] = None
    is_verified_by_doctor: bool = False
    updated_at: Optional[datetime] = None

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "user_full_name": "Ahmet Yılmaz",
                "restaurant_name": "Yemekhane A",
                "suspected_order_id": "123e4567-e89b-12d3-a456-426614174000",
                "symptoms": "Mide bulantısı, baş ağrısı",
                "severity_level": 3,
                "status": "INVESTIGATING",
                "report_date": "2026-02-09T17:55:48.579Z",
                "admin_notes": "İnceleniyor",
                "is_verified_by_doctor": False,
                "updated_at": "2026-02-09T18:00:00.000Z"
            }]
        }
    }


class AdminIncidentListResponse(BaseModel):
    """Admin incident listesi yanıtı."""
    total: int
    page: int
    limit: int
    items: list[AdminIncidentListItem]


class AdminIncidentUpdateRequest(BaseModel):
    """Admin incident güncelleme isteği."""
    status: Optional[str] = Field(None, description="PENDING, INVESTIGATING, CONFIRMED, DISMISSED")
    admin_notes: Optional[str] = Field(None, max_length=2000)
