"""
Incident Schemas - Sağlık Vakası API (TASK-BE-015)
"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class IncidentReportRequest(BaseModel):
    """Sağlık vakası bildirimi isteği."""
    suspected_order_id: UUID = Field(..., description="Şüpheli sipariş ID")
    symptoms: str = Field(..., min_length=10, max_length=2000, description="Belirtiler")
    severity_level: int = Field(..., ge=1, le=5, description="Ciddiyet (1-5)")


class IncidentReportResponse(BaseModel):
    """Sağlık vakası bildirimi yanıtı."""
    incident_id: UUID
    next_steps: list[str] = Field(default_factory=list)
