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

    def test_ocr_confusion_i_and_one(self):
        """OCR I/l karışıklığı düzeltilir (1O5 -> 105)."""
        text = """
        Restoran
        Toplam: 1O5 TL
        """
        result = parse_receipt_text(text)
        assert result.total_amount == 105.0

    def test_multiline_total_format(self):
        """Toplam: ayrı satırda, tutar sonraki satırda."""
        text = """
        Cafe Y
        Toplam:
        78,50 TL
        """
        result = parse_receipt_text(text)
        assert result.total_amount == 78.50

    def test_date_yyyy_mm_dd_format(self):
        """Tarih YYYY-MM-DD formatı."""
        text = """
        Restoran
        2026-03-15 14:30
        Toplam: 50.00
        """
        result = parse_receipt_text(text)
        assert result.receipt_date is not None
        assert result.receipt_date.year == 2026
        assert result.receipt_date.month == 3
        assert result.receipt_date.day == 15
        assert result.receipt_date.hour == 14
        assert result.receipt_date.minute == 30

    def test_items_skip_phone_and_support(self):
        """Telefon, destek hattı satırları ürün olarak parse edilmez."""
        text = """
        Restoran
        +90 555 123 4567
        Destek Hattı: 0850 xxx
        1x Pizza 45.00 TL
        Toplam: 45.00
        """
        result = parse_receipt_text(text)
        assert len(result.items) == 1
        assert result.items[0]["name"] == "Pizza"

    def test_item_name_lahmacun_2_format(self):
        """Lahmacun 2 45.00 formatı (ad başta, miktar ortada)."""
        text = """
        Test
        Lahmacun 2 45.00
        Toplam: 90.00
        """
        result = parse_receipt_text(text)
        assert len(result.items) >= 1
        item = result.items[0]
        assert item["quantity"] == 2
        assert item["unit_price"] == 45.0

    def test_skip_patterns_restaurant_name(self):
        """Fiş, Sipariş gibi kelimeler restoran adı olarak alınmaz; ilk geçerli satır alınır."""
        text = """
        Gerçek Restoran
        Fiş
        Sipariş Kodu: ABC123
        Toplam: 100 TL
        """
        result = parse_receipt_text(text)
        assert result.restaurant_name == "GERÇEK RESTORAN"


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


class TestYemeksepetiScreenshot:
    """Yemeksepeti ekran görüntüsü parse testleri (gerçek dünya senaryoları)."""

    def test_yemeksepeti_dominos_full(self):
        """
        Gerçek Yemeksepeti ekran görüntüsü senaryosu:
        - 'Yardım Merkezi' restoran adı olarak alınmamalı
        - 18:17 saati fiyat olarak algılanmamalı
        - Restoran: Domino's Pizza, Toplam: 250.00 TL
        """
        text = """
        Yardım Merkezi
        Sipariş numarası #c90p-2603-wa1d
        15 Oca 18:17 tarihinde teslim edildi
        Siparişin verildiği yer:
        Domino's Pizza
        Teslim edildiği yer:
        Dedekorkut Konya Şeker Sanayi Ve Ticaret A.Ş 25
        Meram Konya 42090
        1x Pizza X-Large 550,00 TL
        1x X-Large Cheddar Sos (80 gr.) 85,00 TL
        Ara Toplam 620,00 TL
        İndirim -120,00 TL
        KDV dahil 33,64 TL
        Kupon: sepet - 250,00 TL
        Toplam (KDV dahil) 250,00 TL
        Ödeme şekli:
        Online Ödeme 250,00 TL
        Faturayı indir
        """
        result = parse_receipt_text(text)

        # Restoran adı 'Yardım Merkezi' değil, 'Domino's Pizza' olmalı
        assert result.restaurant_name is not None
        assert "DOMINO" in result.restaurant_name
        assert "YARDIM" not in result.restaurant_name
        assert "MERKEZİ" not in (result.restaurant_name or "")

        # Toplam tutar 18.17 (saat) değil, 250.00 olmalı
        assert result.total_amount == 250.0

    def test_yemeksepeti_restaurant_inline(self):
        """Siparişin verildiği yer: Restoran Ad aynı satırda."""
        text = """
        Yardım Merkezi
        Siparişin verildiği yer: Burger King
        Toplam (KDV dahil) 180,50 TL
        """
        result = parse_receipt_text(text)
        assert result.restaurant_name == "BURGER KING"
        assert result.total_amount == 180.50

    def test_time_not_parsed_as_price(self):
        """Saat formatı (18:17) fiyat olarak algılanmamalı."""
        text = """
        Test Restoran
        15 Oca 18:17 tarihinde teslim edildi
        Toplam: 95,00 TL
        """
        result = parse_receipt_text(text)
        assert result.total_amount == 95.0
        assert result.total_amount != 18.17

    def test_ui_blacklist_filtering(self):
        """UI metinleri ('Yardım Merkezi', 'Geri', 'Sepetim') restoran adı olarak alınmamalı."""
        text = """
        Geri
        Yardım Merkezi
        Sepetim
        Gerçek Restoran Adı
        Toplam: 100,00 TL
        """
        result = parse_receipt_text(text)
        assert result.restaurant_name == "GERÇEK RESTORAN ADI"

    def test_toplam_kdv_dahil_priority(self):
        """'Toplam (KDV dahil)' en yüksek öncelikli anahtar kelime olmalı."""
        text = """
        Restoran X
        Ara Toplam 620,00 TL
        İndirim -120,00 TL
        KDV dahil 33,64 TL
        Toplam (KDV dahil) 250,00 TL
        """
        result = parse_receipt_text(text)
        assert result.total_amount == 250.0

    def test_odenecek_tutar_keyword(self):
        """'Ödenecek Tutar' anahtar kelimesi doğru algılanmalı."""
        text = """
        Restoran Y
        Ara Toplam 500,00 TL
        İndirim -100,00 TL
        Ödenecek Tutar: 400,00 TL
        """
        result = parse_receipt_text(text)
        assert result.total_amount == 400.0

    def test_getir_style_receipt(self):
        """Getir tarzı fiş formatı."""
        text = """
        Sipariş Özeti
        Restoran: McDonald's
        2x Big Mac 190,00 TL
        1x Kola 25,00 TL
        Toplam Tutarı 215,00 TL
        """
        result = parse_receipt_text(text)
        assert result.restaurant_name == "MCDONALD'S"
        assert result.total_amount == 215.0


class TestGetirScreenshot:
    """Getir ekran görüntüsü parse testleri (gerçek dünya senaryoları)."""

    def test_getir_odenen_tutar(self):
        """
        Getir sipariş ekranı: 'Ödenen Tutar' doğru algılanmalı.
        'Sipariş Tutarı' (indirim öncesi) alınmamalı.
        """
        text = """
        GetirYemek
        Sipariş Tutarı 440,00 TL
        Kazancın -290,00 TL
        Ödenen Tutar 150,00 TL
        """
        result = parse_receipt_text(text)
        assert result.total_amount == 150.0
        assert result.total_amount != 440.0

    def test_getir_siparis_tutari_blacklisted(self):
        """'Sipariş Tutarı' fiyat kara listesinde, toplam olarak alınmamalı."""
        text = """
        GetirYemek
        Sipariş Tutarı 500,00 TL
        İndirim -100,00 TL
        Ödenen Tutar 400,00 TL
        """
        result = parse_receipt_text(text)
        assert result.total_amount == 400.0

    def test_getir_with_ara_toplam(self):
        """Ara Toplam da toplam olarak alınmamalı."""
        text = """
        Restoran Z
        1x Hamburger 120,00 TL
        1x Patates 40,00 TL
        Ara Toplam 160,00 TL
        Kupon -30,00 TL
        Ödenen Tutar 130,00 TL
        """
        result = parse_receipt_text(text)
        assert result.total_amount == 130.0

    def test_getir_full_receipt(self):
        """Tam Getir fiş senaryosu — restoran adı + doğru tutar."""
        text = """
        Geçmiş Siparişlerim
        GetirYemek
        Restoran: Popeyes
        Sipariş Tutarı 440,00 TL
        Kazancın -290,00 TL
        Ödenen Tutar 150,00 TL
        Ödeme Yöntemi: Kredi Kartı
        """
        result = parse_receipt_text(text)
        assert result.restaurant_name == "POPEYES"
        assert result.total_amount == 150.0

    def test_getir_no_discount(self):
        """Getir fişi indirim olmadan — Sipariş Tutarı = Ödenen Tutar."""
        text = """
        GetirYemek
        Restoran: Burger King
        Sipariş Tutarı 200,00 TL
        Ödenen Tutar 200,00 TL
        """
        result = parse_receipt_text(text)
        assert result.total_amount == 200.0

    def test_getir_kazancin_not_parsed_as_item(self):
        """'Kazancın' satırı ürün olarak parse edilmemeli."""
        text = """
        Restoran: Test
        1x Pizza 300,00 TL
        Sipariş Tutarı 300,00 TL
        Kazancın -150,00 TL
        Ödenen Tutar 150,00 TL
        """
        result = parse_receipt_text(text)
        item_names = [i["name"].lower() for i in result.items]
        assert not any("kazanc" in n or "sipariş tutar" in n for n in item_names)


class TestTrendyolScreenshot:
    """Trendyol Yemek ekran görüntüsü parse testleri (çoklu görsel dahil)."""

    def test_trendyol_single_page(self):
        """Trendyol tek sayfa fiş — Restoran: ve Toplam: doğru algılanmalı."""
        text = """
        Trendyol Yemek
        Restoran: Dayı Döner Kumru (Ferhuniye)
        1x İskender 130,00 TL
        1x Ayran 20,00 TL
        Ara Toplam 150,00 TL
        Toplam: 150,00 TL
        """
        result = parse_receipt_text(text)
        assert result.restaurant_name is not None
        assert "DAYI DÖNER KUMRU" in result.restaurant_name
        assert result.total_amount == 150.0

    def test_trendyol_with_discount(self):
        """Trendyol indirimli fiş — Ara Toplam değil, Toplam alınmalı."""
        text = """
        Trendyol Yemek
        Restoran: Dayı Döner Kumru (Ferhuniye)
        2x İskender 260,00 TL
        2x Ayran 40,00 TL
        1x Künefe 90,00 TL
        1x Mercimek Çorbası 40,00 TL
        1x Pide 90,00 TL
        Ara Toplam 520,00 TL
        İndirim -150,00 TL
        Toplam: 370,00 TL
        """
        result = parse_receipt_text(text)
        assert result.restaurant_name is not None
        assert "DAYI DÖNER" in result.restaurant_name
        assert result.total_amount == 370.0
        assert result.total_amount != 520.0

    def test_trendyol_multi_page_concat(self):
        """
        Trendyol 2 sayfa birleştirilmiş — --- ayırıcı ile.
        Restoran adı ilk sayfada, Toplam ikinci sayfada.
        """
        text = """Trendyol Yemek
Restoran: Dayı Döner Kumru (Ferhuniye)
2x İskender 260,00 TL
2x Ayran 40,00 TL
1x Künefe 90,00 TL
---
1x Mercimek Çorbası 40,00 TL
1x Pide 90,00 TL
Ara Toplam 520,00 TL
İndirim -150,00 TL
Toplam: 370,00 TL"""
        result = parse_receipt_text(text)
        assert result.restaurant_name is not None
        assert "DAYI DÖNER KUMRU" in result.restaurant_name
        assert result.total_amount == 370.0

    def test_trendyol_ui_blacklisted(self):
        """'Trendyol Yemek' restoran adı olarak alınmamalı."""
        text = """
        Trendyol Yemek
        Restoran: Pizza Lazza
        Toplam: 200,00 TL
        """
        result = parse_receipt_text(text)
        assert result.restaurant_name == "PIZZA LAZZA"
        assert "TRENDYOL" not in (result.restaurant_name or "")

    def test_trendyol_restaurant_with_parens(self):
        """Parantezli restoran adı doğru algılanmalı."""
        text = """
        Restoran: Burger King (Kızılay Şube)
        Toplam: 180,00 TL
        """
        result = parse_receipt_text(text)
        assert result.restaurant_name is not None
        assert "BURGER KING" in result.restaurant_name
        assert "KIZILAY" in result.restaurant_name

    def test_trendyol_ara_toplam_blacklisted(self):
        """'Ara Toplam' kesinlikle nihai tutar olarak alınmamalı."""
        text = """
        Restoran: Test Restoran
        1x Döner 130,00 TL
        Ara Toplam 130,00 TL
        İndirim -30,00 TL
        Toplam: 100,00 TL
        """
        result = parse_receipt_text(text)
        assert result.total_amount == 100.0

    def test_all_platforms_regression(self):
        """
        Regresyon testi: Yemeksepeti, Getir ve Trendyol birlikte çalışmalı.
        Her platform kendi formatını korumalı.
        """
        # Yemeksepeti
        ys_text = """
        Siparişin verildiği yer:
        Domino's Pizza
        Toplam (KDV dahil) 250,00 TL
        """
        ys = parse_receipt_text(ys_text)
        assert "DOMINO" in ys.restaurant_name
        assert ys.total_amount == 250.0

        # Getir
        gt_text = """
        Restoran: Popeyes
        Sipariş Tutarı 440,00 TL
        Kazancın -290,00 TL
        Ödenen Tutar 150,00 TL
        """
        gt = parse_receipt_text(gt_text)
        assert gt.restaurant_name == "POPEYES"
        assert gt.total_amount == 150.0

        # Trendyol
        ty_text = """
        Restoran: Dayı Döner Kumru (Ferhuniye)
        Ara Toplam 520,00 TL
        Toplam: 370,00 TL
        """
        ty = parse_receipt_text(ty_text)
        assert "DAYI DÖNER" in ty.restaurant_name
        assert ty.total_amount == 370.0


class TestFoodContent:
    """food_content özet alanı testleri."""

    def test_food_content_from_standard_items(self):
        """Standart ürün satırlarından food_content oluşturulur."""
        text = """
        Restoran X
        2x Lahmacun 45.00 TL
        1x Ayran 10.00 TL
        Toplam: 100.00
        """
        result = parse_receipt_text(text)
        assert result.food_content is not None
        assert "2x Lahmacun" in result.food_content
        assert "1x Ayran" in result.food_content

    def test_food_content_none_when_no_items(self):
        """Ürün yoksa food_content None olmalı."""
        text = """
        Restoran X
        Toplam: 100.00 TL
        """
        result = parse_receipt_text(text)
        assert result.food_content is None

    def test_food_content_yemeksepeti_format(self):
        """Yemeksepeti formatında food_content doğru oluşturulur."""
        text = """
        Siparişin verildiği yer:
        Domino's Pizza
        1x Pizza X-Large 550,00 TL
        1x X-Large Cheddar Sos (80 gr.) 85,00 TL
        Ara Toplam 620,00 TL
        Toplam (KDV dahil) 250,00 TL
        """
        result = parse_receipt_text(text)
        assert result.food_content is not None
        assert "1x Pizza X-Large" in result.food_content
        assert "Cheddar Sos" in result.food_content

    def test_food_content_comma_separated(self):
        """Birden fazla ürün virgülle ayrılır."""
        text = """
        Restoran
        3x Döner 60.00
        2x Cola 20.00
        Toplam: 100.00
        """
        result = parse_receipt_text(text)
        assert result.food_content is not None
        assert ", " in result.food_content
        assert "3x Döner" in result.food_content
        assert "2x Cola" in result.food_content


class TestPlatformItemPatterns:
    """Platform-spesifik ürün kalıpları testleri (Getir, Trendyol)."""

    def test_getir_item_with_trailing_quantity(self):
        """Getir formatı: 'Yok Böyle Menü 1' — satır sonunda adet."""
        text = """
        Restoran: Popeyes
        Yok Böyle Menü 1
        Ödenen Tutar 150,00 TL
        """
        result = parse_receipt_text(text)
        assert len(result.items) >= 1
        item = next((i for i in result.items if "Menü" in i["name"] or "Menu" in i["name"]), None)
        assert item is not None
        assert item["quantity"] == 1
        assert result.food_content is not None
        assert "Menü" in result.food_content or "Menu" in result.food_content

    def test_getir_multiple_items(self):
        """Getir birden fazla ürün."""
        text = """
        Restoran: Burger King
        Whopper Menü 2
        Nuggets 6'lı 1
        Ödenen Tutar 300,00 TL
        """
        result = parse_receipt_text(text)
        assert len(result.items) >= 1
        assert result.food_content is not None

    def test_trendyol_adet_format(self):
        """Trendyol formatı: 'Bol Bol Kumru Adet: 4'."""
        text = """
        Restoran: Dayı Döner Kumru
        Bol Bol Kumru Adet: 4
        Toplam: 200,00 TL
        """
        result = parse_receipt_text(text)
        assert len(result.items) >= 1
        item = next((i for i in result.items if "Kumru" in i["name"]), None)
        assert item is not None
        assert item["quantity"] == 4
        assert result.food_content is not None
        assert "4x Bol Bol Kumru" in result.food_content

    def test_trendyol_adet_with_price(self):
        """Trendyol formatı fiyatlı: 'Bol Bol Kumru Adet: 4 120,00 TL'."""
        text = """
        Restoran: Dayı Döner Kumru
        Bol Bol Kumru Adet: 4 120,00 TL
        Toplam: 480,00 TL
        """
        result = parse_receipt_text(text)
        assert len(result.items) >= 1
        item = next((i for i in result.items if "Kumru" in i["name"]), None)
        assert item is not None
        assert item["quantity"] == 4
        assert item["unit_price"] == 120.0

    def test_mixed_platform_items_food_content(self):
        """Karışık format ürünlerinden food_content oluşturulur."""
        text = """
        Restoran: Test
        2x İskender 130,00 TL
        1x Ayran 20,00 TL
        Toplam: 280,00 TL
        """
        result = parse_receipt_text(text)
        assert result.food_content == "2x İskender, 1x Ayran"


class TestRealWorldOCR:
    """Gerçek ekran görüntüsü OCR metinlerinden platform-spesifik parsing testleri."""

    # ── Yemeksepeti gerçek dünya senaryoları ──────────────────────────────────

    def test_yemeksepeti_real_dominos_food_content(self):
        """
        Yemeksepeti Domino's ekran görüntüsü:
        1x Pizza X-Large ve 1x X-Large Cheddar Sos doğru ayrıştırılmalı.
        """
        text = """
        Yardım Merkezi
        Sipariş numarası #c90p-2603-wa1d
        15 Oca 18:17 tarihinde teslim edildi
        Siparişin verildiği yer:
        Domino's Pizza
        Teslim edildiği yer:
        Dedekorkut Konya Şeker Sanayi Ve Ticaret A.Ş 25
        Meram Konya 42090
        1x Pizza X-Large 550,00 TL
        Bol Malzemos (XL) (sarımsaklı kenar i...
        1x X-Large Cheddar Sos (80 gr.) 85,00 TL
        Ara Toplam 620,00 TL
        İndirim -120,00 TL
        KDV dahil 33,64 TL
        Kupon: sepet - 250,00 TL
        Toplam (KDV dahil) 250,00 TL
        Ödeme şekli:
        Online Ödeme 250,00 TL
        Faturayı indir
        """
        result = parse_receipt_text(text)
        assert result.food_content is not None
        assert "1x Pizza X-Large" in result.food_content
        assert "Cheddar Sos" in result.food_content
        # Boş dönmemeli (eski hata)
        assert len(result.items) >= 2
        assert result.total_amount == 250.0
        assert "DOMINO" in result.restaurant_name

    def test_yemeksepeti_nx_strips_price(self):
        """Yemeksepeti Nx satırında fiyat temizlenip sadece yemek adı alınmalı."""
        text = """
        Siparişin verildiği yer:
        Burger King
        1x Whopper Menü 220,00 TL
        2x Nuggets 6'lı 75,00 TL
        Toplam (KDV dahil) 370,00 TL
        """
        result = parse_receipt_text(text)
        assert len(result.items) == 2
        names = [i["name"] for i in result.items]
        assert "Whopper Menü" in names
        assert "Nuggets 6'lı" in names
        # Fiyat yemek adından çıkarılmış olmalı
        assert all("TL" not in n for n in names)
        assert all("," not in n for n in names)

    # ── Getir gerçek dünya senaryoları ────────────────────────────────────────

    def test_getir_real_sepet_section(self):
        """
        Getir ekran görüntüsü: 'Sepet' bölümünden yemek adı çıkarılmalı.
        Açıklama satırları (Tercihi, Gramaj vb.) atlanmalı.
        """
        text = """
        Sipariş Detayı
        Maydonoz Döner, Meram (Yenişehir Mah.)
        Restoran Kuryesi
        Sepet
        Yok Böyle Menü 1
        Tavuk Dürüm Tercihi: Tavuk Döner Medium Dürüm;
        Gramaj Tercihi: 75 g Mayonez Tercihi: Sarımsaklı
        Mayonez Soğan Tercihi: Soğansız ...
        440,00 TL
        Ödeme Detayı
        Sipariş Tutarı 440,00 TL
        Kazancın 290,00 TL
        Ödenen Tutar 150,00 TL
        """
        result = parse_receipt_text(text)
        assert result.food_content is not None
        assert "Yok Böyle Menü" in result.food_content
        assert len(result.items) >= 1
        item = result.items[0]
        assert item["name"] == "Yok Böyle Menü"
        assert item["quantity"] == 1
        # Açıklama satırları ürün olarak alınmamalı
        item_names = [i["name"].lower() for i in result.items]
        assert not any("tercihi" in n for n in item_names)
        assert not any("gramaj" in n for n in item_names)

    def test_getir_sepet_multiple_items(self):
        """Getir Sepet bölümünde birden fazla yemek olabilir."""
        text = """
        Restoran Kuryesi
        Sepet
        Whopper Menü 2
        Nuggets 6'lı 1
        Ödeme Detayı
        Sipariş Tutarı 300,00 TL
        Ödenen Tutar 300,00 TL
        """
        result = parse_receipt_text(text)
        assert len(result.items) >= 2
        assert result.food_content is not None
        assert "2x Whopper Menü" in result.food_content
        assert "Nuggets" in result.food_content

    # ── Trendyol gerçek dünya senaryoları ─────────────────────────────────────

    def test_trendyol_real_multiline_adet(self):
        """
        Trendyol ekran görüntüsü: Yemek adı üst satırda, Adet: N alt satırda.
        'Bol Bol Kumru' + 'Adet: 4' → 4x Bol Bol Kumru
        """
        text = """
        Sipariş Detay
        Dayı Döner Kumru (Ferhuniye)
        Tekrarla
        Asistan
        Sipariş No: #10880363823
        Sipariş Tarihi: 15 Ocak 2026 / 11:55
        Teslimat: 4 Ürün Teslim Edildi
        Toplam: 370 TL
        Teslimat: Trendyol Go
        Teslimat No: 9459664013
        Restoran: Dayı Döner Kumru (Ferhuniye)
        4 Ürün Teslim Edildi
        Siparişiniz 15 Ocak Perşembe günü saat 12:28'de teslim edilmiştir.
        Bol Bol Kumru
        Adet: 4
        130 TL
        """
        result = parse_receipt_text(text)
        assert result.food_content is not None
        assert "4x Bol Bol Kumru" in result.food_content
        assert len(result.items) >= 1
        item = next((i for i in result.items if "Kumru" in i["name"]), None)
        assert item is not None
        assert item["quantity"] == 4
        # Alakasız satırlar (Sipariş Tarihi vb.) ürün olarak alınmamalı
        item_names = [i["name"].lower() for i in result.items]
        assert not any("sipariş" in n for n in item_names)
        assert not any("teslimat" in n for n in item_names)

    def test_trendyol_multiline_adet_with_price(self):
        """Trendyol multi-line format: fiyat Adet: N satırının altında."""
        text = """
        Trendyol Yemek
        Restoran: Dayı Döner Kumru (Ferhuniye)
        Bol Bol Kumru
        Adet: 4
        130,00 TL
        Toplam: 520,00 TL
        """
        result = parse_receipt_text(text)
        assert len(result.items) >= 1
        item = next((i for i in result.items if "Kumru" in i["name"]), None)
        assert item is not None
        assert item["quantity"] == 4
        assert item["unit_price"] == 130.0

    def test_trendyol_no_false_items(self):
        """
        Trendyol OCR'da 'Adet:', 'Sipariş Tarihi' vb. satırlar
        yanlışlıkla yemek adı olarak alınmamalı.
        """
        text = """
        Trendyol Yemek
        Sipariş No: #12345
        Sipariş Tarihi: 15 Ocak 2026
        Teslimat: 2 Ürün Teslim Edildi
        Lavaş Döner
        Adet: 2
        İç Ayran
        Adet: 1
        Toplam: 300,00 TL
        """
        result = parse_receipt_text(text)
        assert len(result.items) == 2
        names = [i["name"] for i in result.items]
        assert "Lavaş Döner" in names
        assert "İç Ayran" in names
        # Yanlış ürünler olmamalı
        assert "Sipariş Tarihi" not in names
        assert "Sipariş No" not in names
        quantities = {i["name"]: i["quantity"] for i in result.items}
        assert quantities["Lavaş Döner"] == 2
        assert quantities["İç Ayran"] == 1

    def test_trendyol_multipage_deduplication(self):
        """
        Trendyol çift sayfa birleştirme: 2 ekran görüntüsünden gelen aynı
        yemek satırı tekrarlanmamalı (4x Bol Bol Kumru yalnızca bir kez).
        """
        text = """
        Sipariş Detay
        Dayı Döner Kumru (Ferhuniye)
        Sipariş No: #10880363823
        Sipariş Tarihi: 15 Ocak 2026 / 11:55
        Teslimat: 4 Ürün Teslim Edildi
        Toplam: 370 TL
        Restoran: Dayı Döner Kumru (Ferhuniye)
        4 Ürün Teslim Edildi
        Siparişiniz 15 Ocak Perşembe günü saat 12:28'de teslim edilmiştir.
        Bol Bol Kumru
        Adet: 4
        130 TL
        ---
        Sipariş Detay
        4 Ürün Teslim Edildi
        Siparişiniz 15 Ocak Perşembe günü saat 12:28'de teslim edilmiştir.
        Bol Bol Kumru
        Adet: 4
        130 TL
        Sipariş Notu
        Servis İstiyorum
        Teslimat Adresi
        Toplam: 370 TL
        """
        result = parse_receipt_text(text)
        assert result.food_content is not None
        # Tekrar olmamalı — yalnızca bir kez
        assert result.food_content.count("4x Bol Bol Kumru") == 1
        assert result.food_content == "4x Bol Bol Kumru"
        # items listesinde de tekrar olmamalı
        kumru_items = [i for i in result.items if "Kumru" in i["name"]]
        assert len(kumru_items) == 1

    def test_yemeksepeti_leading_whitespace_food_content(self):
        """
        Yemeksepeti: Satır başında boşluk/tab olsa bile 1x Pizza bulunmalı.
        OCR bazen satır başına boşluk ekler.
        """
        text = """
        Yardım Merkezi
        Siparişin verildiği yer:
        Domino's Pizza
           1x Pizza X-Large 550,00 TL
           1x X-Large Cheddar Sos (80 gr.) 85,00 TL
        Toplam (KDV dahil) 250,00 TL
        """
        result = parse_receipt_text(text)
        assert result.food_content is not None
        assert "1x Pizza X-Large" in result.food_content
        assert "Cheddar Sos" in result.food_content
        assert len(result.items) >= 2
        # Fiyat yemek adından çıkarılmış olmalı
        names = [i["name"] for i in result.items]
        assert all("550" not in n for n in names)
        assert all("TL" not in n for n in names)

    def test_yemeksepeti_real_dominos_nonempty(self):
        """
        Yemeksepeti Domino's: food_content kesinlikle boş dönmemeli.
        Bu regresyon testi — eski hata tekrarlamasın.
        """
        text = """
        Yardım Merkezi
        Sipariş numarası #c90p-2603-wa1d
        15 Oca 18:17 tarihinde teslim edildi
        Siparişin verildiği yer:
        Domino's Pizza
        Teslim edildiği yer:
        Dedekorkut Konya Şeker Sanayi Ve Ticaret A.Ş 25
        Meram Konya 42090
        1x Pizza X-Large 550,00 TL
        Bol Malzemos (XL) (sarımsaklı kenar i...
        1x X-Large Cheddar Sos (80 gr.) 85,00 TL
        Ara Toplam 620,00 TL
        İndirim -120,00 TL
        KDV dahil 33,64 TL
        Kupon: sepet - 250,00 TL
        Toplam (KDV dahil) 250,00 TL
        Ödeme şekli:
        Online Ödeme 250,00 TL
        Faturayı indir
        """
        result = parse_receipt_text(text)
        # food_content boş dönmemeli — eski hata
        assert result.food_content is not None
        assert result.food_content != ""
        assert "Pizza X-Large" in result.food_content
        assert "Cheddar Sos" in result.food_content
