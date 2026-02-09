"""
TASK-QA-001: Schema validation tests
Pydantic schema'ları - veritabanı gerektirmez.
"""
import pytest
from datetime import datetime
from uuid import uuid4

from app.schemas.order import (
    AdminOrderListItem,
    AdminOrderListResponse,
    OrderHistoryItemSchema,
    OrderHistoryEntrySchema,
)
from app.schemas.incident import AdminIncidentUpdateRequest


class TestAdminOrderListItem:
    """AdminOrderListItem schema testleri."""

    def test_valid_order_list_item(self):
        """Geçerli order list item oluşturulur."""
        item = AdminOrderListItem(
            id=uuid4(),
            student_name="Ahmet Yılmaz",
            restaurant_name="Pasaport Pizza",
            declared_at=datetime.now(),
            total_amount=85.50,
            method="SCREENSHOT",
        )
        assert item.student_name == "Ahmet Yılmaz"
        assert item.restaurant_name == "Pasaport Pizza"
        assert item.total_amount == 85.50
        assert item.method == "SCREENSHOT"

    def test_order_list_item_restaurant_null(self):
        """restaurant_name None olabilir."""
        item = AdminOrderListItem(
            id=uuid4(),
            student_name="Test",
            restaurant_name=None,
            declared_at=datetime.now(),
            total_amount=None,
            method="MANUAL_ENTRY",
        )
        assert item.restaurant_name is None
        assert item.total_amount is None


class TestAdminOrderListResponse:
    """AdminOrderListResponse schema testleri."""

    def test_valid_list_response(self):
        """Geçerli list response."""
        items = [
            AdminOrderListItem(
                id=uuid4(),
                student_name="User",
                restaurant_name="Rest",
                declared_at=datetime.now(),
                total_amount=50.0,
                method="PHYSICAL_RECEIPT",
            )
        ]
        resp = AdminOrderListResponse(total=1, page=1, limit=20, items=items)
        assert resp.total == 1
        assert resp.page == 1
        assert resp.limit == 20
        assert len(resp.items) == 1


class TestOrderHistoryItemSchema:
    """OrderHistoryItemSchema testleri."""

    def test_valid_item(self):
        """Geçerli ürün satırı."""
        item = OrderHistoryItemSchema(
            item_name="Pizza",
            quantity=2,
            unit_price=45.00,
        )
        assert item.item_name == "Pizza"
        assert item.quantity == 2
        assert item.unit_price == 45.00


class TestAdminIncidentUpdateRequest:
    """AdminIncidentUpdateRequest schema testleri."""

    def test_valid_update(self):
        """Geçerli incident güncelleme."""
        req = AdminIncidentUpdateRequest(
            status="CONFIRMED",
            admin_notes="İncelendi",
        )
        assert req.status == "CONFIRMED"
        assert req.admin_notes == "İncelendi"

    def test_admin_notes_optional(self):
        """admin_notes opsiyonel."""
        req = AdminIncidentUpdateRequest(status="DISMISSED")
        assert req.admin_notes is None
