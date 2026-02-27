"""
OCR Text Parser - Platform Bazlı Zeki Ayrıştırıcı (TASK-BE-009)

Geliştirilmiş Pipeline:
  1. Platform Tespiti      → Trendyol / Getir / Yemeksepeti / Genel
  2. Çöp Metin Filtreleme  → Çapa (anchor) tabanlı satır atlama
  3. İçerik Yakalama       → Nx regex + alt-açıklama birleştirme
  4. Tutar Yakalama        → Anahtar kelime öncelikli fiyat algılama

─────────────────────────────────────────────────
Nasıl Test Edilir?  (Admin Panel → UI Üzerinden)
─────────────────────────────────────────────────
1. Backend + Admin Panel'i başlatın:
      cd Proje && docker-compose up -d
      cd Proje/admin-panel && npm run dev

2. Admin panelde oturum açın:
      http://localhost:3000/login
      TCKN: 11111111111  |  Şifre: Admin123!

3. Sipariş yükleme sayfasını açın veya Swagger UI kullanın:
      http://localhost:8000/docs → POST /v1/orders/upload

4. Farklı platform fişleri ile test edin:
      - Yemeksepeti ekran görüntüsü  (1x, 2x satırları, Toplam KDV dahil)
      - Getir ekran görüntüsü        (Sepet bölümü, Ödenen Tutar)
      - Trendyol ekran görüntüsü     (Adet: N formatı)
      - Bulanık kağıt fiş fotoğrafı
    - Soluk / buruşuk termal kağıt fiş

5. Response'ta kontrol edin:
      - restaurant_name → doğru restoran mı? (müşteri adı değil!)
      - food_content    → ürünler doğru mu? (adres/telefon yok mu?)
      - total_amount    → doğru tutar mı? (indirim öncesi değil!)

İpucu: Teslimat adresi, müşteri adı gibi çöp metinlerin artık
       yemek veya restoran olarak algılanmadığını doğrulayın.
Not: Restoran adı bulunamazsa sistem artık hata fırlatmak yerine
    "Bilinmeyen Restoran (Kağıt Fiş)" ile parse işlemine devam eder.
─────────────────────────────────────────────────
"""
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import logging
from app.services.exceptions import ReceiptProcessingError

logger = logging.getLogger(__name__)

USER_FACING_PARSE_ERROR = (
    "Fiş okunamadı veya restoran tespit edilemedi, lütfen daha net bir görüntü yükleyin"
)


@dataclass
class ParsedReceipt:
    """Fiş parse sonucu."""
    restaurant_name: Optional[str] = None
    total_amount: Optional[float] = None
    receipt_date: Optional[datetime] = None
    items: list[dict] = None  # [{"name": str, "quantity": int, "unit_price": Optional[float]}]
    food_content: Optional[str] = None  # "1x Pizza X-Large, 1x Cheddar Sos"

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

# ── Çöp Metin Çapaları (Junk Anchors) ────────────────────────────────────────
# Bu kalıplardan biriyle eşleşen satır VE ardından gelen N satır atlanır.
# Böylece teslimat adresi, müşteri adı, sipariş notu gibi çöp metinler
# yemek veya restoran adı olarak algılanmaz.
# Format: (regex_pattern, lines_to_skip_after_anchor)
_JUNK_ANCHOR_PATTERNS = [
    # ── Müşteri bilgileri (müşteri adı restoran sanılmasın) ──
    (r"müşteri\s*bilgi", 1),
    (r"müşteri\s*ad[ıi]", 1),
    (r"müşter.*ileti[sş]", 1),
    # ── Adres bilgileri (adres yemek sanılmasın) ──
    (r"teslim\s*edildi[gğ]i\s*yer", 2),   # "Teslim edildiği yer:" + 2 satır adres
    (r"teslimat\s*adres", 2),              # "Teslimat Adresi:" + 2 satır adres
    (r"teslim\s*adres", 2),
    (r"fatura\s*adres", 2),
    # ── Sipariş kaynağı (restoran tespiti için ayrı kullanılır, item'da atlanır) ──
    (r"sipari[sş]in\s*verildi[gğ]i\s*yer", 1),
    # ── Sipariş meta bilgileri ──
    (r"sipari[sş]\s*notu", 1),             # "Sipariş Notu:" + not metni
    (r"sipari[sş]\s*no\s*[:#]", 0),        # Sadece kendi satırı
    (r"sipari[sş]\s*kodu", 0),
    (r"sipari[sş]\s*numaras", 0),
    # ── Ödeme bilgileri ──
    (r"[oö]deme\s*[sş]ekli", 1),           # "Ödeme şekli:" + ödeme yöntemi
    (r"[oö]deme\s*y[oö]ntemi", 1),
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

# Trendyol kağıt fişlerinde restoran adı bazen önekli gelir:
# "TRENDYOL-Meşhur Unkapanı Pilavcısı"
TRENDYOL_PREFIX_RE = re.compile(r"^\s*trendyol\s*[-:]+\s*(.+?)\s*$", re.IGNORECASE)

# Fallback restoran adayı içinde bu yemek türleri varsa restoran olarak alma.
FALLBACK_FOOD_KEYWORDS_RE = re.compile(
    r"\b(d[üu]r[üu]m|pizza|men[üu]|porsiyon|lahmacun|[cç]orba)\b",
    re.IGNORECASE,
)

UNKNOWN_PAPER_RECEIPT_RESTAURANT = "Bilinmeyen Restoran (Kağıt Fiş)"
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

# ── Platform-spesifik ürün kalıpları ──────────────────────────────────────────
# Yemeksepeti: "1x Pizza X-Large (80 gr.)" — zaten ITEM_PATTERNS[0] ile yakalanır.
# Trendyol:    "Bol Bol Kumru Adet: 4" — "Adet:" etiketli
TRENDYOL_ITEM_PATTERNS = [
    # Trendyol fiyatlı: "Bol Bol Kumru Adet: 4 120,00 TL" (önce kontrol — daha spesifik)
    (r"^(.+?)\s+[Aa]det\s*:\s*(\d+)\s+([\d,\.]+)\s*(?:tl|₺|€)?$", "trendyol_price"),
    # Trendyol fiyatsız: "Bol Bol Kumru Adet: 4" veya "Bol Bol Kumru Adet:4"
    (r"^(.+?)\s+[Aa]det\s*:\s*(\d+)\s*$", "trendyol"),
]

# Getir: "Yok Böyle Menü 1" — satır sonunda adet (fiyatsız, çok genel kalıp — en sonda kontrol)
GETIR_TRAILING_QTY_RE = re.compile(r"^(.+?)\s+(\d+)\s*$")


# ── Platform Tespiti ──────────────────────────────────────────────────────────
# Her platformun kendine özgü sinyal kelimeleri ve ağırlıkları.
_YEMEKSEPETI_SIGNALS = [
    (r"sipari[sş]in\s*verildi[gğ]i\s*yer", 3),
    (r"yard[iı]m\s*merkezi", 2),
    (r"faturay[iı]\s*indir", 2),
    (r"sipari[sş]\s*numaras[iı]\s*#", 2),
    (r"teslim\s*edildi[gğ]i\s*yer", 1),
    (r"[oö]deme\s*[sş]ekli", 1),
    (r"online\s*[oö]deme", 1),
]

_GETIR_SIGNALS = [
    (r"getiryemek|getir\s*yemek", 3),
    (r"restoran\s*kuryesi", 3),
    (r"[oö]deme\s*detay[iı]?", 2),
    (r"kazan[cç][iı]?n", 2),
    (r"[oö]denen\s*tutar", 2),
]

_TRENDYOL_SIGNALS = [
    (r"trendyol", 3),
    (r"teslimat\s*no\s*:", 2),
    (r"[uü]r[uü]n\s*teslim\s*edildi", 2),
]

# Trendyol: önceki satır kontrolü — bu kalıpları içeren satırlar yemek adı değildir.
_TRENDYOL_SKIP_PREV_LINE = [
    r"sipari[sş]", r"teslimat", r"toplam", r"indirim",
    r"[oö]deme", r"restoran", r"fla[sş]", r"kupon",
    r"trendyol", r"ara\s*toplam", r"kdv",
    r"teslim\s*edil", r"g[uü]n[uü]\s*saat",
]

# Getir: Sepet bölümündeki açıklama satırlarını atla.
_GETIR_DESCRIPTION_SKIP = [
    r"tercihi",
    r"gramaj",
    r"malzeme",
    r"ekstra",
]


# ── Çöp Metin Filtresi ───────────────────────────────────────────────────────

def _get_junk_indices(lines: list[str]) -> set[int]:
    """
    Çapa (anchor) tabanlı çöp indekslerini hesapla.

    Bir çapa satırı eşleştiğinde, o satır + ardından gelen N satır
    çöp olarak işaretlenir.  Böylece adres, müşteri adı, sipariş notu
    gibi bilgiler yemek/restoran olarak algılanmaz.

    Returns:
        Atlanması gereken satır indekslerinin kümesi.
    """
    junk: set[int] = set()
    i = 0
    while i < len(lines):
        line_lower = lines[i].strip().lower()
        matched = False
        for pattern, skip_after in _JUNK_ANCHOR_PATTERNS:
            if re.search(pattern, line_lower):
                junk.add(i)
                for j in range(1, skip_after + 1):
                    if i + j < len(lines):
                        junk.add(i + j)
                i += skip_after  # Atlanan satırları geç
                matched = True
                break
        if not matched:
            pass
        i += 1
    return junk


def _build_item_candidate_lines(lines: list[str]) -> list[str]:
    """
    Item (ürün) ayrıştırması için temizlenmiş satır listesi oluştur.
    Çöp çapalarını ve takipçi satırlarını kaldırır.
    """
    junk = _get_junk_indices(lines)
    return [lines[i] for i in range(len(lines)) if i not in junk]


def _is_sub_description(line: str) -> bool:
    """
    Satırın bir önceki yemeğin alt-açıklaması olup olmadığını kontrol et.

    Alt-açıklama = Nx kalıbı YOK + fiyat etiketi YOK + uzunluk > 2.
    Örnek: "Bol Malzemos (XL) (sarımsaklı kenar i..."
    """
    if not line or len(line) < 3:
        return False
    # Nx kalıbı varsa → yeni ürün, alt-açıklama değil
    if re.search(r'\d+\s*[xX×]', line):
        return False
    # Fiyat etiketi varsa → alt-açıklama değil
    if re.search(r'[\d,\.]+\s*(?:tl|₺|€)', line, re.IGNORECASE):
        return False
    # Toplam/özet satırıysa → alt-açıklama değil
    if any(re.search(p, line, re.IGNORECASE) for p in ITEM_SKIP_PATTERNS):
        return False
    return True


def _detect_platform(lines: list[str]) -> str:
    """
    OCR metninden platform tespiti yap.
    Sinyal ağırlıklarına göre en olası platformu döndürür.

    Returns: 'yemeksepeti', 'getir', 'trendyol', or 'generic'
    """
    full_text_lower = " ".join(lines).lower()

    ys_score = sum(w for p, w in _YEMEKSEPETI_SIGNALS if re.search(p, full_text_lower))
    gt_score = sum(w for p, w in _GETIR_SIGNALS if re.search(p, full_text_lower))
    ty_score = sum(w for p, w in _TRENDYOL_SIGNALS if re.search(p, full_text_lower))

    # Ek sinyaller: satır bazlı kontrol
    for line in lines:
        line_lower = line.strip().lower()
        # "Sepet" tek başına bir satır → güçlü Getir sinyali
        if re.match(r'^sepet$', line_lower):
            gt_score += 3
        # "Adet: N" → güçlü Trendyol sinyali
        if re.search(r'adet\s*:\s*\d+', line_lower):
            ty_score += 3

    max_score = max(ys_score, gt_score, ty_score)
    if max_score < 1:
        return "generic"

    # En yüksek skor kazanır (eşitlikte Trendyol > Getir > Yemeksepeti)
    if ty_score == max_score:
        return "trendyol"
    elif gt_score == max_score:
        return "getir"
    elif ys_score == max_score:
        return "yemeksepeti"
    return "generic"


# ── Platform-Spesifik Ürün Ayrıştırıcıları ────────────────────────────────────

# Yemeksepeti: Fiyat pattern'leri — satır sonundan re.sub ile temizlenir
# Geniş fiyat temizleme: küsuratlı (örn: 550,00 TL) veya küsuratsız (85 TL) sayıları yakalar
_YEMEKSEPETI_PRICE_STRIP_RE = re.compile(
    r'\s+\d[\d\s,\.]*\s*(?:tl|₺|€|t[lıl]?)\s*$',
    re.IGNORECASE,
)
_YEMEKSEPETI_BARE_PRICE_STRIP_RE = re.compile(
    r'\s+(\d[\d,\.]+)\s*$',
)
# Yemeksepeti Nx kalıbı: case-insensitive, boşluk toleranslı
_YEMEKSEPETI_ITEM_RE = re.compile(r'(\d+)\s*[xX×]\s+(.*)', re.IGNORECASE)


def _parse_items_yemeksepeti(lines: list[str]) -> list[dict]:
    r"""
    Yemeksepeti formatı: Satırlarda '(\d+)x Yemek Adı [Fiyat TL]' kalıbı aranır.
    - Büyük/küçük harf duyarsız (?i) — '1X' ve '1x' aynı.
    - Satır başında boşluk/karakter olabilir (^ yok, re.search).
    - Eşleşen metinden fiyat kısmı re.sub ile güvenli şekilde silinir.
    - Alt-açıklama satırları (Nx yok, fiyat yok) önceki ürüne eklenir.
    """
    items = []
    for idx, line in enumerate(lines):
        line_stripped = line.strip()
        m = _YEMEKSEPETI_ITEM_RE.search(line_stripped)
        if not m:
            # Nx eşleşmedi — alt-açıklama olabilir mi?
            if items and _is_sub_description(line_stripped):
                # Önceki ürünün alt-açıklaması olarak ekle
                items[-1]["name"] += f" ({line_stripped})"
            continue

        try:
            qty = int(m.group(1))
            rest = m.group(2).strip()
            if qty < 1 or qty > 99 or not rest:
                continue

            # Fiyatı re.sub ile temizle: "Pizza X-Large 550,00 TL" → "Pizza X-Large"
            unit_price = None

            # Önce TL/₺ etiketli fiyatı ara ve çıkar
            price_match = _YEMEKSEPETI_PRICE_STRIP_RE.search(rest)
            if price_match:
                raw_price = price_match.group(0).strip()
                unit_price = _safe_parse_amount(raw_price)
                name = _YEMEKSEPETI_PRICE_STRIP_RE.sub('', rest).strip()
            else:
                # TL etiketi olmadan küsuratlı sayı ile biten ("Lahmacun 45.00")
                bare_match = _YEMEKSEPETI_BARE_PRICE_STRIP_RE.search(rest)
                if bare_match:
                    possible_price = _safe_parse_amount(bare_match.group(1))
                    possible_name = _YEMEKSEPETI_BARE_PRICE_STRIP_RE.sub('', rest).strip()
                    if possible_name and possible_price and possible_price > 1:
                        name = possible_name
                        unit_price = possible_price
                    else:
                        name = rest
                else:
                    name = rest

            if len(name) > 1:
                items.append({"name": name, "quantity": qty, "unit_price": unit_price})

        except (ValueError, AttributeError, IndexError) as e:
            # OCR hatalı satırı atla, diğer satırlara devam et
            logger.debug(f"Yemeksepeti item parse hatası atlandı: {e}")
            continue

    return items


def _parse_items_getir(lines: list[str]) -> list[dict]:
    """
    Getir formatı: 'Sepet' bölümünden sonra, 'Ödeme Detayı'/'Sipariş Tutarı'na kadar.
    Ürün satırı: 'Yok Böyle Menü 1' (satır sonunda adet).
    Açıklama satırları (Tercihi:, Gramaj vb.) atlanır.
    """
    items = []

    # ── Adım 1: "Sepet" bölümünü bul ─────────────────────────────────────────
    sepet_idx = -1
    end_idx = len(lines)

    for i, line in enumerate(lines):
        line_lower = line.strip().lower()
        if re.match(r'^sepet$', line_lower):
            sepet_idx = i
        elif sepet_idx >= 0 and re.search(
            r'[oö]deme\s*detay|sipari[sş]\s*tutar',
            line_lower,
        ):
            end_idx = i
            break

    if sepet_idx < 0:
        return items  # "Sepet" bulunamadı → boş döndür

    # ── Adım 2: Sepet – Ödeme Detayı arası satırları tara ────────────────────
    for i in range(sepet_idx + 1, end_idx):
        line_stripped = lines[i].strip()
        if not line_stripped:
            continue

        # Fiyat satırlarını atla (sadece TL ile biten)
        if re.search(r'[\d,\.]+\s*(?:tl|₺)\s*$', line_stripped, re.IGNORECASE):
            continue

        # Açıklama satırlarını atla (Tercihi:, Gramaj vb.)
        if any(re.search(p, line_stripped, re.IGNORECASE) for p in _GETIR_DESCRIPTION_SKIP):
            continue

        # Trailing quantity: "Yok Böyle Menü 1"
        m = re.match(r'^(.+?)\s+(\d+)\s*$', line_stripped)
        if m:
            name = m.group(1).strip()
            qty = int(m.group(2))
            if len(name) > 1 and 1 <= qty <= 99:
                items.append({"name": name, "quantity": qty, "unit_price": None})
                continue

        # Miktar belirtilmemiş → qty=1
        if len(line_stripped) > 2:
            items.append({"name": line_stripped, "quantity": 1, "unit_price": None})

    return items


def _parse_items_trendyol(lines: list[str]) -> list[dict]:
    """
    Trendyol formatı: Yemek adı üst satırda, 'Adet: N' alt satırda.
    Ayrıca aynı satırda 'Yemek Adet: N [Fiyat TL]' formatını da destekler.

    Kural: lines[i] satırı Adet:\\s*(\\d+) ile eşleşiyorsa:
      - Adet: öncesinde metin varsa → aynı satırdaki metin yemek adı
      - Yoksa → lines[i-1] yemek adı
    'Sipariş Tarihi' gibi alakasız satırlar filtrelenir.
    """
    items = []
    used_indices: set[int] = set()  # Zaten kullanılan satır indeksleri

    for i, line in enumerate(lines):
        line_stripped = line.strip()
        m = re.search(r'[Aa]det\s*:\s*(\d+)', line_stripped)
        if not m:
            continue

        qty = int(m.group(1))
        if qty < 1 or qty > 99:
            continue

        # Adet: öncesindeki metin (aynı satırda yemek adı var mı?)
        before_adet = line_stripped[:m.start()].strip()

        if before_adet and len(before_adet) > 1:
            # "Bol Bol Kumru Adet: 4" — aynı satırda
            name = before_adet
        elif i > 0 and (i - 1) not in used_indices:
            # "Adet: 4" ayrı satırda → önceki satır yemek adı
            prev_line = lines[i - 1].strip()

            # Önceki satır alakasız mı kontrol et
            if len(prev_line) < 2:
                continue
            if _is_blacklisted_ui_text(prev_line):
                continue
            if any(re.search(p, prev_line, re.IGNORECASE) for p in _TRENDYOL_SKIP_PREV_LINE):
                continue

            name = prev_line
            used_indices.add(i - 1)
        else:
            continue

        # Adet: N'den sonraki metin (aynı satırda fiyat var mı?)
        after_adet = line_stripped[m.end():].strip()
        unit_price = None
        if after_adet:
            price_match = re.search(r'([\d\.,]+)\s*(?:tl|₺|€)?', after_adet, re.IGNORECASE)
            if price_match:
                unit_price = _safe_parse_amount(price_match.group(1))

        # Aynı satırda fiyat yoksa, bir sonraki satıra bak
        if unit_price is None and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            price_match = re.match(r'^([\d\.,]+)\s*(?:tl|₺|€)\s*$', next_line, re.IGNORECASE)
            if price_match:
                unit_price = _safe_parse_amount(price_match.group(1))

        items.append({"name": name, "quantity": qty, "unit_price": unit_price})
        used_indices.add(i)

    return items


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
    """
    Ürün listesi çıkar.

    Akış:
      1. Platform tespiti (tüm satırlarla)
      2. Çöp çapalarını filtrele → temiz satır listesi oluştur
      3. Temiz satırları platforma özel parser'a ver
      4. Bulamazsa genel (generic) parser'a düş
    """
    platform = _detect_platform(lines)
    logger.debug(f"Platform tespit edildi: {platform}")

    # Çöp metin çapalarını filtrele (adres, müşteri adı, sipariş notu vb.)
    clean_lines = _build_item_candidate_lines(lines)
    logger.debug(f"Çöp filtresi: {len(lines)} satır → {len(clean_lines)} temiz satır")

    items: list[dict] = []

    if platform == "yemeksepeti":
        items = _parse_items_yemeksepeti(clean_lines)
    elif platform == "getir":
        items = _parse_items_getir(clean_lines)
    elif platform == "trendyol":
        items = _parse_items_trendyol(clean_lines)

    # Platform-spesifik parser bulamadıysa genel parser'a düş
    if not items:
        items = _parse_items_generic(clean_lines)

    # ── Tekilleştirme (Deduplication) ─────────────────────────────────────────
    # Çoklu ekran görüntüsü birleştirildiğinde aynı yemek birden fazla
    # kez çıkabilir (özellikle Trendyol). Aynı isim+miktar çiftini tekle.
    items = _deduplicate_items(items)

    return items


def _deduplicate_items(items: list[dict]) -> list[dict]:
    """
    Aynı yemek adı ve miktarına sahip ürünleri tekilleştir.
    İlk bulunan kaydı tutar (fiyat bilgisi varsa onu tercih eder).
    """
    if not items:
        return items

    seen: dict[str, int] = {}  # key → items_deduped index
    items_deduped: list[dict] = []

    for item in items:
        key = f"{item.get('quantity', 1)}x {item.get('name', '')}"
        if key in seen:
            # Eğer mevcut kayıtta fiyat yoksa ama yeni kayıtta varsa, güncelle
            existing_idx = seen[key]
            if items_deduped[existing_idx].get("unit_price") is None and item.get("unit_price") is not None:
                items_deduped[existing_idx]["unit_price"] = item["unit_price"]
            continue  # Tekrarı atla
        seen[key] = len(items_deduped)
        items_deduped.append(item)

    return items_deduped


def _parse_items_generic(lines: list[str]) -> list[dict]:
    """Genel ürün ayrıştırıcı — platform tespit edilemediğinde fallback."""
    items = []
    for line in lines:
        line = line.strip()
        if len(line) < 3:
            continue
        # Telefon, destek hattı vb. satırları atla
        if any(re.search(p, line, re.IGNORECASE) for p in ITEM_SKIP_PATTERNS):
            continue

        matched = False

        # ── 1) Trendyol "Adet:" kalıpları (en spesifik — önce) ──────────────
        for pattern, platform in TRENDYOL_ITEM_PATTERNS:
            m = re.match(pattern, line, re.IGNORECASE)
            if m:
                g = m.groups()
                if platform == "trendyol_price" and len(g) == 3:
                    name = g[0].strip()
                    qty = int(g[1])
                    try:
                        price_clean = g[2].replace(",", ".")
                        price_clean = _normalize_ocr_number(price_clean)
                        unit_price = float(price_clean)
                        if 0 < unit_price <= MAX_UNIT_PRICE and len(name) > 1:
                            items.append({"name": name, "quantity": qty, "unit_price": unit_price})
                            matched = True
                    except ValueError:
                        if len(name) > 1:
                            items.append({"name": name, "quantity": qty, "unit_price": None})
                            matched = True
                elif platform == "trendyol" and len(g) == 2:
                    name = g[0].strip()
                    qty = int(g[1])
                    if 1 <= qty <= 99 and len(name) > 1:
                        items.append({"name": name, "quantity": qty, "unit_price": None})
                        matched = True
                break

        if matched:
            continue

        # ── 2) Standart kalıplar (fiyatlı — Yemeksepeti vb.) ─────────────────
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
                        matched = True
                except ValueError:
                    pass
                break

        if matched:
            continue

        # ── 3) Getir trailing qty (en genel — en sonda) ──────────────────────
        # "Yok Böyle Menü 1" — satır sonunda adet, fiyat yok
        m = GETIR_TRAILING_QTY_RE.match(line)
        if m:
            name = m.group(1).strip()
            qty = int(m.group(2))
            if 1 <= qty <= 99 and len(name) > 1:
                items.append({"name": name, "quantity": qty, "unit_price": None})

    return items


def _build_food_content(items: list[dict]) -> Optional[str]:
    """
    Ürün listesinden okunabilir sipariş içeriği özeti oluştur.
    Örnek: "1x Pizza X-Large, 1x Cheddar Sos, 2x Ayran"
    Tekrar eden ürünler otomatik olarak tekilleştirilir.
    """
    if not items:
        return None
    parts: list[str] = []
    for item in items:
        qty = item.get("quantity", 1)
        name = item.get("name", "")
        if name:
            parts.append(f"{qty}x {name}")
    # food_content string düzeyinde de tekilleştir (sıra korunur)
    parts = list(dict.fromkeys(parts))
    return ", ".join(parts) if parts else None


def _is_blacklisted_ui_text(text: str) -> bool:
    """Metnin uygulama arayüzü (UI) kara listesinde olup olmadığını kontrol et."""
    normalized = text.strip().lower()
    # Tam eşleşme veya kara liste ifadesini içeriyor mu?
    for bl in UI_BLACKLIST:
        if bl == normalized or bl in normalized:
            return True
    return False


def _normalize_prefixed_restaurant_name(text: str) -> str:
    """TRENDYOL- benzeri önekleri temizleyip restoran adını döndür."""
    if not text:
        return ""
    s = text.strip()
    m = TRENDYOL_PREFIX_RE.match(s)
    if m:
        return m.group(1).strip()
    return s


def _is_food_like_candidate(text: str) -> bool:
    """Fallback adayında bariz yemek türü varsa True döndür."""
    if not text:
        return False
    return bool(FALLBACK_FOOD_KEYWORDS_RE.search(text))


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

        # 1A) TRENDYOL- prefix formatı: doğrudan restoran adı gibi kabul et
        prefixed = _normalize_prefixed_restaurant_name(line_stripped)
        if prefixed != line_stripped and len(prefixed) >= 2 and not _is_blacklisted_ui_text(prefixed):
            return prefixed

        for kw_pattern in RESTAURANT_KEYWORD_PATTERNS:
            kw_match = re.search(kw_pattern, line_stripped, re.IGNORECASE)
            if kw_match:
                # Anahtar kelimeden sonra aynı satırda metin var mı?
                after_kw = _normalize_prefixed_restaurant_name(line_stripped[kw_match.end():].strip())
                if after_kw and len(after_kw) >= 2 and not _is_blacklisted_ui_text(after_kw):
                    return after_kw
                # Bir sonraki satırı kontrol et
                if i + 1 < len(lines):
                    next_line = _normalize_prefixed_restaurant_name(lines[i + 1].strip())
                    if (
                        len(next_line) >= 2
                        and not _is_blacklisted_ui_text(next_line)
                        and not any(re.search(p, next_line, re.IGNORECASE) for p in SKIP_PATTERNS)
                    ):
                        return next_line

    # ── Aşama 2: İlk anlamlı satır (fallback) ───────────────────────────────
    # Çöp çapalarıyla işaretlenmiş satırları da atla (müşteri adı, adres vb.)
    junk = _get_junk_indices(lines)
    candidates = []
    for i, line in enumerate(lines):
        line = line.strip()
        if len(line) < 2:
            continue
        # Çapa tabanlı çöp indekslerini atla (müşteri adı restoran sanılmasın)
        if i in junk:
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
        # Fallback'te bariz yemek türleri restoran adı olamaz
        if _is_food_like_candidate(line):
            continue
        # İlk 10 satır içinde, makul uzunlukta (2-60 karakter)
        if i < 10 and 2 <= len(line) <= 60:
            candidates.append(_normalize_prefixed_restaurant_name(line))
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
        raise ReceiptProcessingError(USER_FACING_PARSE_ERROR, "PARSER_UNREADABLE")

    try:
        lines = [l.strip() for l in raw_text.split("\n") if l.strip()]

        # \u00c7oklu g\u00f6rsel ay\u0131r\u0131c\u0131s\u0131n\u0131 (---) atla (multi-page OCR birle\u015ftirme)
        lines = [l for l in lines if l != "---"]

        if not lines:
            raise ReceiptProcessingError(USER_FACING_PARSE_ERROR, "PARSER_UNREADABLE")

        restaurant_name = _extract_restaurant_name(lines)
        total_amount = _parse_total(lines)
        receipt_date = _parse_date(lines)
        items = _parse_items(lines)
        food_content = _build_food_content(items)

        # Kritik güncelleme: restoran tespit edilemese de parse akışını kesme.
        if not restaurant_name:
            restaurant_name = UNKNOWN_PAPER_RECEIPT_RESTAURANT

        restaurant_name = _normalize_restaurant_name(restaurant_name)

        # Ek güvenlik: tamamen alakasız içerikte boş parse sonucu oluşmasın
        if total_amount is None and not items and not food_content:
            raise ReceiptProcessingError(USER_FACING_PARSE_ERROR, "PARSER_UNREADABLE")

        return ParsedReceipt(
            restaurant_name=restaurant_name,
            total_amount=total_amount,
            receipt_date=receipt_date,
            items=items,
            food_content=food_content,
        )
    except ReceiptProcessingError:
        raise
    except Exception as e:
        logger.exception("Receipt parsing failed: %s", e)
        raise ReceiptProcessingError(USER_FACING_PARSE_ERROR, "PARSER_UNREADABLE")


class ParserService:
    """Parser service facade."""

    def parse(self, raw_text: str) -> ParsedReceipt:
        return parse_receipt_text(raw_text)


parser_service = ParserService()
