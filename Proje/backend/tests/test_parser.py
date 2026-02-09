"""
TASK-QA-001: Parser Service Unit Tests
OCR metin parse mantığı - veritabanı gerektirmez.
"""
import pytest
from datetime import datetime

from app.services.parser_service import (
    parse_receipt_text,
    ParserService,
    ParsedReceipt,
)


class TestParseReceipt:
    """parse_receipt_text fonksiyon testleri."""

    def test_empty_text_returns_empty_receipt(self):
        """Boş veya whitespace metin boş ParsedReceipt döner."""
        result = parse_receipt_text("")
        assert result.restaurant_name is None
        assert result.total_amount is None
        assert result.receipt_date is None
        assert result.items == []

        result2 = parse_receipt_text("   \n\t  ")
        assert result2.restaurant_name is None
        assert result2.items == []

    def test_restaurant_name_extraction(self, sample_receipt_text):
        """Restoran ismi ilk anlamlı satırdan çıkarılır."""
        result = parse_receipt_text(sample_receipt_text)
        assert result.restaurant_name == "PASAPORT PIZZA"

    def test_total_amount_extraction(self, sample_receipt_text):
        """Toplam tutar doğru parse edilir."""
        result = parse_receipt_text(sample_receipt_text)
        assert result.total_amount == 115.0

    def test_total_amount_with_turkish_format(self):
        """Toplam: 156,50 TL formatı."""
        text = """
        Test Restoran
        Toplam: 156,50 TL
        """
        result = parse_receipt_text(text)
        assert result.total_amount == 156.50

    def test_total_amount_with_dot_separator(self):
        """Toplam 99.99 formatı."""
        text = """
        Cafe X
        Genel Toplam 99.99 TL
        """
        result = parse_receipt_text(text)
        assert result.total_amount == 99.99

    def test_items_extraction(self, sample_receipt_text):
        """Ürün listesi doğru parse edilir."""
        result = parse_receipt_text(sample_receipt_text)
        assert len(result.items) >= 1
        # İlk ürün: Karışık Pizza
        names = [i["name"] for i in result.items]
        assert any("Pizza" in n or "pizza" in n.lower() for n in names)

    def test_receipt_date_extraction(self, sample_receipt_text):
        """Tarih parse edilir (varsa)."""
        result = parse_receipt_text(sample_receipt_text)
        assert result.receipt_date is not None
        assert isinstance(result.receipt_date, datetime)
        assert result.receipt_date.year == 2026
        assert result.receipt_date.month == 1
        assert result.receipt_date.day == 21

    def test_items_with_quantity(self):
        """2x Ürün Adı 45.00 formatı."""
        text = """
        Restoran
        2x Lahmacun 45.00 TL
        Toplam: 90.00
        """
        result = parse_receipt_text(text)
        assert len(result.items) >= 1
        item = result.items[0]
        assert item["quantity"] == 2
        assert item["unit_price"] == 45.0

    def test_ocr_confusion_o_and_zero(self):
        """OCR O/0 karışıklığı düzeltilir (156,OO -> 156.00)."""
        text = """
        Test
        Toplam: 156,OO TL
        """
        result = parse_receipt_text(text)
        assert result.total_amount == 156.0


class TestParserService:
    """ParserService facade testleri."""

    def test_parser_service_parse(self):
        """ParserService.parse() parse_receipt_text ile aynı sonucu verir."""
        service = ParserService()
        text = "Restoran X\nToplam: 50.00 TL"
        result = service.parse(text)
        assert isinstance(result, ParsedReceipt)
        assert result.restaurant_name == "RESTORAN X"
        assert result.total_amount == 50.0
