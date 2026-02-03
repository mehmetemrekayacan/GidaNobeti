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

# Toplam tutar pattern'leri (OCR bazen ₺ yerine € okuyabilir, O/0 karışıklığı)
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


def _parse_total(lines: list[str]) -> Optional[float]:
    """Toplam tutarı bul. OCR O/0, l/1 karışıklığını düzeltir. Toplam: ve 156,OOt ayrı satırlarda olabilir."""
    # Önce "Toplam:" sonrası satırı kontrol et (çok satırlı format)
    for i, line in enumerate(lines):
        if re.search(r"^(?:toplam|total)[:\s]*$", line.strip(), re.IGNORECASE) and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            m = re.search(r"^([\d\s,\.OoIl]+)\s*(?:tl|₺|€|t)?", next_line, re.IGNORECASE)
            if m:
                num_str = m.group(1).replace(" ", "").replace(",", ".")
                num_str = _normalize_ocr_number(num_str)
                try:
                    val = float(num_str)
                    if 0 < val < 10_000_000:  # Makul tutar
                        return val
                except ValueError:
                    pass
    # Tek satırda arama
    for line in lines:
        line_lower = line.lower().strip()
        for pattern in TOTAL_PATTERNS:
            m = re.search(pattern, line_lower, re.IGNORECASE)
            if m:
                num_str = m.group(1).replace(" ", "").replace(",", ".")
                num_str = _normalize_ocr_number(num_str)
                try:
                    val = float(num_str)
                    if 0 < val < 10_000_000:
                        return val
                except ValueError:
                    continue
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


def _extract_restaurant_name(lines: list[str]) -> Optional[str]:
    """
    Restoran ismini çıkar. Genelde ilk anlamlı satır veya 'Restoran'/'Cafe' içeren.
    """
    candidates = []
    for i, line in enumerate(lines):
        line = line.strip()
        if len(line) < 2:
            continue
        # Hariç tut
        if any(re.search(p, line, re.IGNORECASE) for p in SKIP_PATTERNS):
            continue
        if re.match(r"^[\d\s,\.]+$", line):
            continue
        # İlk 5 satır içinde, makul uzunlukta (2-50 karakter)
        if i < 5 and 2 <= len(line) <= 50:
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
