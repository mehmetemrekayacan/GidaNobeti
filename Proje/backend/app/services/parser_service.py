"""
OCR Text Parser - Fiş metninden yapılandırılmış veri çıkarma (TASK-BE-009)
"""
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import logging

logger = logging.getLogger(__name__)


@dataclass
class ParsedReceipt:
    """Fiş parse sonucu."""
    restaurant_name: Optional[str] = None
    total_amount: Optional[float] = None
    receipt_date: Optional[datetime] = None
    items: list[dict] = None  # [{"name": str, "quantity": int, "unit_price": Optional[float]}]

    def __post_init__(self):
        if self.items is None:
            self.items = []


# Restoran ismi için hariç tutulacak kelimeler (fiş başlıkları)
SKIP_PATTERNS = [
    r"^f[iı]ş$", r"^fis$", r"^receipt$", r"^toplam$", r"^total$",
    r"^\d+\.\d+\.\d+", r"^\d{2}:\d{2}", r"^[\d\s,\.]+$",
    r"^kdv", r"^vergi", r"^t[eé]şekk[uü]r", r"^thank",
    r"^sipari[sş]\s*kodu", r"^sipari[sş]\s*notu", r"^sipari[sş]\s*numaras", r"^sipari[sş]\s*nurnaras",  # OCR "siparis" yazabilir
    r"^müşteri\s*bilg", r"^müşter.*iletiş",  # Müşteri İletişim (OCR: Müşterl İletişlm)
    r"^ürün$", r"^adet$", r"^tutar$",  # Tablo başlıkları
    r"^\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{2,4}",  # Tarih (10/09/2024)
    r"^\d{4}[\.\/\-]\d{1,2}[\.\/\-]\d{1,2}",   # Tarih (2024-09-10)
    r"^\d{10,}$",  # Sadece telefon numarası
    r"^[A-Za-zÇçĞğİıÖöŞşÜü\s]+[A-Za-zÇçĞğİıÖöŞşÜü]\.$",  # Müşteri adı (Ahmet Emin D.)
]
# ── Uygulama Arayüzü (UI) Kara Listesi ──────────────────────────────────────
# Yemeksepeti, Getir, Trendyol gibi uygulamaların ekran görüntüsünde
# restoran adı olarak algılanmaması gereken standart UI metinleri.
UI_BLACKLIST = [
    "yardım merkezi", "yardim merkezi",
    "sipariş özeti", "siparis ozeti",
    "sipariş numarası", "siparis numarasi",
    "sipariş detayı", "siparis detayi",
    "geri", "ana sayfa", "anasayfa",
    "hesabım", "hesabim",
    "arama", "sepetim", "sepet",
    "online ödeme", "online odeme",
    "ödeme şekli", "odeme sekli",
    "faturayı indir", "faturayi indir",
    "teslim edildi", "teslim edildiği yer",
    "kargo takip", "değerlendir",
    "tekrar sipariş ver", "destek",
    "iletişim", "iletisim",
    "profil", "ayarlar", "bildirimler",
    "çıkış yap", "cikis yap",
    "kampanyalar", "favoriler",
]

# Restoran adını belirlemek için anahtar kelime ipuçları.
# Bu ifadelerden sonra gelen metin (aynı satır veya bir sonraki satır) restoran adıdır.
RESTAURANT_KEYWORD_PATTERNS = [
    r"sipari[sş]in\s*verildi[gğ]i\s*yer\s*[:\-]?",
    r"restoran\s*[:\-]",
    r"i[sş]letme\s*[:\-]",
    r"ma[gğ]aza\s*[:\-]",
    r"[sş]ube\s*[:\-]",
]
# ── Toplam tutar pattern'leri ─────────────────────────────────────────────────
# Öncelik sırasına göre: en spesifik → en genel
# "Toplam (KDV dahil)" gibi kesin ifadeler en yüksek güvenilirliğe sahip.
TOTAL_KEYWORD_PRIORITY = [
    # ── Tier 1: Kesin toplam (indirim/kupon sonrası, nihai ödenen) ──
    r"toplam\s*\(?\s*kdv\s*(?:dahil|d[aâ]hil|dah[iı]l)\s*\)?",
    r"[oö]denen\s*tutar[ıi]?",            # "Ödenen Tutar" (Getir vb.)
    r"[oö]de[nm]ecek\s*tutar[ıi]?",       # "Ödenecek Tutar"
    r"net\s*[oö]denen",                    # "Net Ödenen"
    r"genel\s*toplam",
    r"net\s*toplam",
    # ── Tier 2: Genel toplam (kara liste filtresi uygulanır) ──
    r"toplam\s*tutar[ıi]?",
    r"toplam",
    r"total",
]

# Saat formatını (HH:MM) fiyat olarak algılamayı engellemek için
# Bu pattern, bir sayının saat formatı olup olmadığını kontrol eder.
TIME_FORMAT_RE = re.compile(r"(?:^|\s)(\d{1,2}):(\d{2})(?:\s|$)")

# Fiyat çıkarma: satırdaki son "123,45 TL" / "123.45 ₺" kalıbını yakalar
PRICE_IN_LINE_RE = re.compile(
    r"([\d\s,\.OoIl]+)\s*(?:tl|₺|€|t(?:[lı1])?)"
    r"|(?:tl|₺|€)\s*([\d\s,\.OoIl]+)",
    re.IGNORECASE,
)

# Eski TOTAL_PATTERNS – geriye dönük uyumluluk için hâlâ fallback olarak kullanılır
TOTAL_PATTERNS = [
    r"(?:toplam|total|genel\s*toplam|ara\s*toplam)[:\s]*([\d\s,\.OoIl]+)\s*(?:tl|₺|€|t)?",
    r"([\d\s,\.OoIl]+)\s*(?:tl|₺|€|t)\s*(?:toplam|total)?",
    r"(?:öde[nm]ecek|tutar)[:\s]*([\d\s,\.OoIl]+)",
]

# Tarih pattern'leri
DATE_PATTERNS = [
    r"(\d{2})[\.\/\-](\d{2})[\.\/\-](\d{4})",
    r"(\d{4})[\.\/\-](\d{2})[\.\/\-](\d{2})",
]
TIME_PATTERN = r"(\d{1,2}):(\d{2})"

# unit_price makul üst sınır (TL) - telefon/numara yanlış parse edilmesin, DB NUMERIC(10,2) overflow önle
MAX_UNIT_PRICE = 10000.0

# Ürün satırı: "2x Lahmacun 45.00" veya "Lahmacun 2 45,00" veya "Lahmacun 45 TL" (OCR bazen € okuyabilir)
ITEM_PATTERNS = [
    r"^(\d+)\s*[xX×]\s*(.+?)\s+([\d,\.]+)\s*(?:tl|₺|€)?$",  # 2x Lahmacun 45.00
    r"^(.+?)\s+(\d+)\s+([\d,\.]+)\s*(?:tl|₺|€)?$",           # Lahmacun 2 45.00
    r"^(.+?)\s+([\d,\.]+)\s*(?:tl|₺|€)?$",                   # Lahmacun 45.00
]


def _normalize_ocr_number(s: str) -> str:
    """OCR hatalarını düzelt: O/o->0, I/l->1 (rakam karışıklığı)."""
    if not s:
        return s
    s = s.replace("O", "0").replace("o", "0")
    s = s.replace("I", "1").replace("l", "1")  # sadece sayı bağlamında
    return s


def _normalize_restaurant_name(name: str) -> str:
    """Restoran ismini normalize et (uppercase, trim)."""
    if not name:
        return ""
    s = name.strip().upper()
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def _is_time_format(text: str) -> bool:
    """Metnin saat formatı (HH:MM) içerip içermediğini kontrol et."""
    m = TIME_FORMAT_RE.search(text)
    if m:
        h, mi = int(m.group(1)), int(m.group(2))
        if 0 <= h <= 23 and 0 <= mi <= 59:
            return True
    return False


def _extract_price_from_text(text: str) -> Optional[float]:
    """
    Verilen metinden fiyat değerini çıkar.
    Saat formatlarını (HH:MM) yok sayar.
    Birden fazla fiyat varsa en büyük/son olanı döndürür.
    """
    if _is_time_format(text):
        # Satırda ':' ile saat varsa, sadece saat kısmını kaldırıp kalan fiyatı ara
        cleaned = TIME_FORMAT_RE.sub(" ", text)
        if not cleaned.strip():
            return None
        text = cleaned

    candidates: list[float] = []

    # TL/₺ ile biten tüm fiyatları bul
    for m in PRICE_IN_LINE_RE.finditer(text):
        raw = m.group(1) or m.group(2)
        if raw:
            val = _safe_parse_amount(raw)
            if val is not None:
                candidates.append(val)

    # Doğrudan sayısal değer arama (TL etiketi olmayan durumlar)
    bare_numbers = re.findall(r"([\d,\.OoIl]+)", text)
    for raw in bare_numbers:
        val = _safe_parse_amount(raw)
        if val is not None:
            candidates.append(val)

    if candidates:
        return candidates[-1]  # Son (en alttaki) tutarı tercih et
    return None


def _safe_parse_amount(raw: str) -> Optional[float]:
    """Ham metin parçasını float tutara dönüştür. Geçersizse None döner."""
    num_str = raw.replace(" ", "").replace(",", ".")
    num_str = _normalize_ocr_number(num_str)
    # Birden fazla nokta varsa sadece sonuncusu ondalık ayırıcıdır (1.250.00 → 1250.00)
    parts = num_str.split(".")
    if len(parts) > 2:
        num_str = "".join(parts[:-1]) + "." + parts[-1]
    try:
        val = float(num_str)
        if 0 < val < 10_000_000:
            return val
    except ValueError:
        pass
    return None


# ── Fiyat Satırı Kara Listesi ────────────────────────────────────────────────
# Bu kelimeleri içeren satırlar "nihai tutar" olarak alınmamalıdır.
# İndirim öncesi tutarlar, kupon indirimleri vb. tuzak satırları filtreler.
PRICE_LINE_BLACKLIST_PATTERNS = [
    r"sipari[sş]\s*tutar[ıi]?",     # "Sipariş Tutarı" (indirim öncesi sipariş toplamı)
    r"ara\s*toplam",                 # "Ara Toplam" (subtotal)
    r"kazan[cç]",                    # "Kazancın" (Getir indirim etiketi)
    r"indirim",                      # "İndirim" (discount)
    r"iskonto",                      # "İskonto" (discount)
    r"kupon",                        # "Kupon" (coupon)
    r"sepet\s*tutar",                # "Sepet Tutarı" (cart amount)
]


def _is_blacklisted_price_line(line: str) -> bool:
    """Satırın fiyat kara listesinde olup olmadığını kontrol et.
    Bu satırlardaki tutarlar nihai ödenen tutar değildir."""
    line_lower = line.strip().lower()
    return any(re.search(p, line_lower) for p in PRICE_LINE_BLACKLIST_PATTERNS)


def _parse_total(lines: list[str]) -> Optional[float]:
    """
    Toplam tutarı bul.
    Öncelik sırası:
      1) "Toplam (KDV dahil)" / "Ödenen Tutar" gibi kesin anahtar kelimeler
      2) Genel fallback – eski pattern'ler
    Alttan yukarıya (bottom-up) tarar — nihai tutar her zaman fişin alt kısmındadır.
    Kara listedeki satırları (Sipariş Tutarı, Ara Toplam vb.) atlar.
    Saat formatlarını (HH:MM) fiyat olarak algılamaz.
    """
    n = len(lines)

    # ── Aşama 1: Öncelikli anahtar kelimelerle eşleşme (bottom-up) ──────────
    for keyword_pattern in TOTAL_KEYWORD_PRIORITY:
        for i in range(n - 1, -1, -1):  # Alttan yukarı tara
            line_stripped = lines[i].strip()

            # Kara listedeki satırları atla (Sipariş Tutarı, Ara Toplam vb.)
            if _is_blacklisted_price_line(line_stripped):
                continue

            kw_match = re.search(keyword_pattern, line_stripped, re.IGNORECASE)
            if not kw_match:
                continue

            # Anahtar kelimeden sonraki metin parçasını al
            after_kw = line_stripped[kw_match.end():].strip().lstrip(":").strip()

            # Aynı satırda fiyat var mı?
            if after_kw:
                val = _extract_price_from_text(after_kw)
                if val is not None:
                    return val

            # Bir sonraki satırda fiyat var mı? (çok satırlı format)
            if i + 1 < n:
                val = _extract_price_from_text(lines[i + 1].strip())
                if val is not None:
                    return val

    # ── Aşama 2: Eski fallback pattern'leri (kara liste filtreli) ────────────
    for line in lines:
        line_lower = line.lower().strip()
        # Kara listedeki satırları atla
        if _is_blacklisted_price_line(line):
            continue
        # Saat içeren satırları atla
        if _is_time_format(line):
            continue
        for pattern in TOTAL_PATTERNS:
            m = re.search(pattern, line_lower, re.IGNORECASE)
            if m:
                val = _safe_parse_amount(m.group(1))
                if val is not None:
                    return val
    return None


def _parse_date(lines: list[str]) -> Optional[datetime]:
    """Tarih/saat bul."""
    for line in lines:
        for pattern in DATE_PATTERNS:
            m = re.search(pattern, line)
            if m:
                g = m.groups()
                try:
                    if len(g[0]) == 4:  # YYYY-MM-DD
                        year, month, day = int(g[0]), int(g[1]), int(g[2])
                    else:
                        day, month, year = int(g[0]), int(g[1]), int(g[2])
                    if 1 <= month <= 12 and 1 <= day <= 31:
                        t = re.search(TIME_PATTERN, line)
                        h, mi = (int(t.group(1)), int(t.group(2))) if t else (12, 0)
                        return datetime(year, month, day, h, mi)
                except (ValueError, IndexError):
                    continue
    return None


# Ürün satırı olmayan (telefon, destek hattı, tarih vb.) - bu satırları atla
ITEM_SKIP_PATTERNS = [
    r"destek\s*hatt", r"iletişim", r"telefon", r"\+90\s*\d",
    r"^\d{10,}$",  # Sadece 10+ rakam (telefon)
    r"sipariş\s*kodu", r"müşteri\s*bilg", r"müşteri\s*iletişim",
    r"^\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{2,4}",  # Tarih (10/09/2024)
    r"(?:^|\s)(?:toplam|total|genel\s*toplam|ara\s*toplam|net\s*toplam)[:\s]",  # Toplam satırları ürün değil
    r"(?:^|\s)(?:indirim|iskonto|kupon)[:\s]",  # İndirim satırları
    r"(?:^|\s)kdv\s*(?:dahil|hariç)?[:\s]",  # KDV satırları
    r"(?:^|\s)(?:öde[nm]ecek|ödeme|ödenen)[:\s]",  # Ödeme/Ödenen satırları
    r"sipari[sş]\s*tutar",                           # Sipariş Tutarı (indirim öncesi)
    r"kazan[cç]",                                    # Kazancın (Getir indirimi)
]


def _parse_items(lines: list[str]) -> list[dict]:
    """Ürün listesi çıkar."""
    items = []
    for line in lines:
        line = line.strip()
        if len(line) < 3:
            continue
        # Telefon, destek hattı vb. satırları atla
        if any(re.search(p, line, re.IGNORECASE) for p in ITEM_SKIP_PATTERNS):
            continue
        # Sayı ile başlayan veya "x" içeren satırları dene
        for pattern in ITEM_PATTERNS:
            m = re.match(pattern, line, re.IGNORECASE)
            if m:
                g = m.groups()
                if len(g) == 3:
                    if g[0].isdigit():
                        qty, name, price = int(g[0]), g[1].strip(), g[2]
                    else:
                        name, qty, price = g[0].strip(), int(g[1]), g[2]
                else:
                    name, price = g[0].strip(), g[1]
                    qty = 1
                try:
                    price_clean = price.replace(",", ".")
                    price_clean = _normalize_ocr_number(price_clean)
                    unit_price = float(price_clean)
                    # Makul fiyat sınırı (telefon numarası vb. yanlış parse önleme)
                    if 0 < unit_price <= MAX_UNIT_PRICE and len(name) > 1:
                        items.append({"name": name, "quantity": qty, "unit_price": unit_price})
                except ValueError:
                    pass
                break
    return items


def _is_blacklisted_ui_text(text: str) -> bool:
    """Metnin uygulama arayüzü (UI) kara listesinde olup olmadığını kontrol et."""
    normalized = text.strip().lower()
    # Tam eşleşme veya kara liste ifadesini içeriyor mu?
    for bl in UI_BLACKLIST:
        if bl == normalized or bl in normalized:
            return True
    return False


def _extract_restaurant_name(lines: list[str]) -> Optional[str]:
    """
    Restoran ismini çıkar.

    Öncelik sırası:
      1) "Siparişin verildiği yer:", "Restoran:" gibi anahtar kelime ipuçları →
         aynı satırdaki devam metni veya bir sonraki satır.
      2) İlk anlamlı satır (kara liste ve skip pattern'ler filtrelendikten sonra).
    """
    # ── Aşama 1: Anahtar kelime tabanlı tespit ───────────────────────────────
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        for kw_pattern in RESTAURANT_KEYWORD_PATTERNS:
            kw_match = re.search(kw_pattern, line_stripped, re.IGNORECASE)
            if kw_match:
                # Anahtar kelimeden sonra aynı satırda metin var mı?
                after_kw = line_stripped[kw_match.end():].strip()
                if after_kw and len(after_kw) >= 2 and not _is_blacklisted_ui_text(after_kw):
                    return after_kw
                # Bir sonraki satırı kontrol et
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if (
                        len(next_line) >= 2
                        and not _is_blacklisted_ui_text(next_line)
                        and not any(re.search(p, next_line, re.IGNORECASE) for p in SKIP_PATTERNS)
                    ):
                        return next_line

    # ── Aşama 2: İlk anlamlı satır (fallback) ───────────────────────────────
    candidates = []
    for i, line in enumerate(lines):
        line = line.strip()
        if len(line) < 2:
            continue
        # Kara listedeki UI metinlerini atla
        if _is_blacklisted_ui_text(line):
            continue
        # Eski skip pattern'leri uygula
        if any(re.search(p, line, re.IGNORECASE) for p in SKIP_PATTERNS):
            continue
        if re.match(r"^[\d\s,\.]+$", line):
            continue
        # Saat/tarih içeren satırları atla
        if _is_time_format(line):
            continue
        # İlk 10 satır içinde, makul uzunlukta (2-60 karakter)
        if i < 10 and 2 <= len(line) <= 60:
            candidates.append(line)
    if candidates:
        return candidates[0]
    return None


def parse_receipt_text(raw_text: str) -> ParsedReceipt:
    """
    OCR ham metninden yapılandırılmış veri çıkar.

    Args:
        raw_text: OCR'dan gelen ham metin

    Returns:
        ParsedReceipt dataclass
    """
    if not raw_text or not raw_text.strip():
        return ParsedReceipt()

    lines = [l.strip() for l in raw_text.split("\n") if l.strip()]

    # \u00c7oklu g\u00f6rsel ay\u0131r\u0131c\u0131s\u0131n\u0131 (---) atla (multi-page OCR birle\u015ftirme)
    lines = [l for l in lines if l != "---"]

    restaurant_name = _extract_restaurant_name(lines)
    total_amount = _parse_total(lines)
    receipt_date = _parse_date(lines)
    items = _parse_items(lines)

    if restaurant_name:
        restaurant_name = _normalize_restaurant_name(restaurant_name)

    return ParsedReceipt(
        restaurant_name=restaurant_name or None,
        total_amount=total_amount,
        receipt_date=receipt_date,
        items=items
    )


class ParserService:
    """Parser service facade."""

    def parse(self, raw_text: str) -> ParsedReceipt:
        return parse_receipt_text(raw_text)


parser_service = ParserService()
