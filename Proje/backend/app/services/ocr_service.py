"""
OCR Service - Fiş/Ekran görüntüsünden metin çıkarma (TASK-BE-008)

Geliştirilmiş pipeline:
  1. Görüntü Ön İşleme  → grayscale, kontrast artırma, keskinleştirme
    2. Binarization         → metni siyah/beyaz ayırma (gölge bastırma)
    3. EasyOCR (detail=1)  → bbox + text + confidence
    4. Y-Ekseni Satır Birleştirme → aynı satırdaki kelimeler yan yana

KVKK: Görsel RAM'de işlenir, diske kaydedilmez.

─────────────────────────────────────────────────
Nasıl Test Edilir?
─────────────────────────────────────────────────
Aşağıdaki adımları izleyerek yeni OCR kalitesini (özellikle bulanık/kağıt fiş
görselleriyle) Postman veya Swagger UI üzerinden test edebilirsiniz:

1. Backend'i çalıştırın:
      cd Proje && docker-compose up -d
   Health check: GET http://localhost:8000/health

2. Swagger UI ile test:
      Tarayıcıda http://localhost:8000/docs adresini açın.
      POST /v1/orders/upload endpoint'ini bulun.
      "Try it out" butonuna tıklayın.
      "files" alanına bulanık bir kağıt fiş fotoğrafı yükleyin (JPEG/PNG, max 5 MB).
      "Execute" butonuna basın.
      Yanıtta dönen `raw_text` alanını inceleyin:
        - Satırlar doğru şekilde birleşmiş mi?
        - Ürün adı ve fiyat aynı satırda mı?
        - Confidence değeri ne kadar?

3. Postman ile test:
      POST http://localhost:8000/v1/orders/upload
      Authorization: Bearer <token>   (login edip token alın)
      Body → form-data:
        Key   = files   (type: File)
        Value = fiş görseli seçin
      Send'e basıp response'taki raw_text ve confidence'ı kontrol edin.

4. cURL ile hızlı test:
      curl -X POST http://localhost:8000/v1/orders/upload \
        -H "Authorization: Bearer <TOKEN>" \
        -F "files=@bulanik_fis.jpg"

İpucu: Aynı fişi eski ve yeni kod ile karşılaştırarak iyileşmeyi ölçün.
         Bulanık, eğik ve düşük çözünürlüklü görseller en iyi test materyalidir.
─────────────────────────────────────────────────
"""

import io
import logging
from typing import List, Tuple

from PIL import Image, ImageEnhance, ImageFilter, UnidentifiedImageError
import numpy as np

from app.core.config import settings
from app.services.exceptions import ReceiptProcessingError

logger = logging.getLogger(__name__)

# ── Sabitler ──────────────────────────────────────────────────────────────────
_reader = None  # Lazy EasyOCR reader

MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024   # 5 MB (KVKK)
MAX_IMAGE_DIMENSION = 1280               # Fiş için yeterli; performans dengesi

# Ön işleme parametreleri — dijital ekran görüntülerini bozmayacak dengeli değerler
_CONTRAST_FACTOR = 1.5    # 1.0 = orijinal, 1.5 = dengeli kontrast (dijital SS bozulmasın)
_SHARPNESS_FACTOR = 1.5   # 1.0 = orijinal, 1.5 = güvenli keskinlik (artifakt yok)
_BRIGHTNESS_FACTOR = 1.1  # Hafif parlaklık artışı (kağıt fişlerde faydalı)
_BINARIZATION_ENABLE = True

# Satır birleştirme toleransı (piksel)
_LINE_Y_TOLERANCE = 15  # Bu değer kadar Y farkı olan kelimeler aynı satırda


# ── EasyOCR Lazy Loader ──────────────────────────────────────────────────────
def _get_reader():
    """Lazy initialize EasyOCR reader (Türkçe + İngilizce)."""
    global _reader
    if _reader is None:
        try:
            import easyocr

            langs = [l.strip() for l in settings.OCR_LANGUAGES.split(",") if l.strip()]
            if not langs:
                langs = ["tr", "en"]
            gpu = settings.OCR_ENABLE_GPU
            logger.info("Initializing EasyOCR: langs=%s, gpu=%s", langs, gpu)
            _reader = easyocr.Reader(langs, gpu=gpu, verbose=False)
        except Exception as e:
            logger.exception("EasyOCR initialization failed: %s", e)
            raise ReceiptProcessingError(
                "Fiş okunamadı veya restoran tespit edilemedi, lütfen daha net bir görüntü yükleyin",
                "OCR_UNREADABLE",
            )
    return _reader


# ── 1. Görüntü Ön İşleme (Preprocessing) ────────────────────────────────────
def _preprocess_image(image_bytes: bytes) -> np.ndarray:
    """
    Görseli EasyOCR'a vermeden önce kalitesini artırmak için ön işleme uygular.

    Pipeline:
      1. Boyut küçültme   → MAX_IMAGE_DIMENSION'a sığdır (LANCZOS)
      2. Gri tonlama      → Renk bilgisini kaldır, OCR için kontrastı netleştir
      3. Kontrast artırma  → Yazıları arka plandan belirgin ayır
      4. Parlaklık ayarı   → Karanlık fişlerde okunabilirliği artır
      5. Keskinleştirme    → Bulanık kenarları netleştir (ImageFilter + Enhance)
            6. Binarization      → Gölgeleri bastırıp metni siyah/beyaza indir

    RAM-only, diske yazma yok (KVKK).

    Args:
        image_bytes: Ham görsel verisi (JPEG/PNG).

    Returns:
        np.ndarray: Ön işlenmiş görüntü (RGB, uint8).

    Raises:
        ReceiptProcessingError: Görsel açılamıyor veya bozuk.
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
    except (UnidentifiedImageError, OSError, ValueError) as e:
        logger.warning("Invalid/corrupt image for OCR: %s", e)
        raise ReceiptProcessingError(
            "Fiş okunamadı veya restoran tespit edilemedi, lütfen daha net bir görüntü yükleyin",
            "OCR_UNREADABLE",
        )
    except Exception as e:
        logger.exception("Unexpected image open error: %s", e)
        raise ReceiptProcessingError(
            "Fiş okunamadı veya restoran tespit edilemedi, lütfen daha net bir görüntü yükleyin",
            "OCR_UNREADABLE",
        )

    # ── Adım 1: Boyut küçültme ───────────────────────────────────────────────
    w, h = img.size
    if max(h, w) > MAX_IMAGE_DIMENSION:
        ratio = MAX_IMAGE_DIMENSION / max(h, w)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.Resampling.LANCZOS)

    # ── Adım 2: Gri tonlama (Grayscale) ──────────────────────────────────────
    img = img.convert("L")  # 8-bit grayscale

    # ── Adım 3: Kontrast artırma ──────────────────────────────────────────────
    img = ImageEnhance.Contrast(img).enhance(_CONTRAST_FACTOR)

    # ── Adım 4: Parlaklık ayarı ──────────────────────────────────────────────
    img = ImageEnhance.Brightness(img).enhance(_BRIGHTNESS_FACTOR)

    # ── Adım 5: Keskinleştirme ───────────────────────────────────────────────
    # Önce kernel-tabanlı sharpen filtresi, sonra Enhance ile ince ayar
    img = img.filter(ImageFilter.SHARPEN)
    img = ImageEnhance.Sharpness(img).enhance(_SHARPNESS_FACTOR)

    # ── Adım 6: Binarization (Kağıt fişler için kritik) ─────────────────────
    if _BINARIZATION_ENABLE:
        gray_arr = np.array(img, dtype=np.uint8)

        # Arka plan gölgelerini bastır: düşük frekanslı aydınlık katmanını çıkar
        background = np.array(
            Image.fromarray(gray_arr).filter(ImageFilter.GaussianBlur(radius=18)),
            dtype=np.float32,
        )
        normalized = np.clip((gray_arr.astype(np.float32) / (background + 1.0)) * 255.0, 0, 255)
        normalized_u8 = normalized.astype(np.uint8)

        # Öncelik: OpenCV varsa adaptif threshold; yoksa numpy Otsu fallback
        binary = None
        try:
            import cv2

            binary = cv2.adaptiveThreshold(
                normalized_u8,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                31,
                12,
            )
            logger.debug("Binarization: OpenCV adaptiveThreshold kullanıldı")
        except Exception:
            # NumPy Otsu fallback (cv2 yoksa)
            hist = np.bincount(normalized_u8.ravel(), minlength=256).astype(np.float64)
            prob = hist / (hist.sum() + 1e-9)
            omega = np.cumsum(prob)
            mu = np.cumsum(prob * np.arange(256))
            mu_t = mu[-1]
            sigma_b = (mu_t * omega - mu) ** 2 / (omega * (1.0 - omega) + 1e-9)
            threshold = int(np.argmax(sigma_b))
            binary = np.where(normalized_u8 > threshold, 255, 0).astype(np.uint8)
            logger.debug("Binarization: NumPy Otsu fallback kullanıldı (thr=%d)", threshold)

        img = Image.fromarray(binary, mode="L")

    # EasyOCR RGB bekler → grayscale'i 3 kanala genişlet
    img_rgb = img.convert("RGB")
    arr = np.array(img_rgb, dtype=np.uint8)

    logger.debug(
        "Preprocessing complete: size=%dx%d, contrast=%.1f, sharpness=%.1f, bin=%s",
        arr.shape[1], arr.shape[0], _CONTRAST_FACTOR, _SHARPNESS_FACTOR, _BINARIZATION_ENABLE,
    )
    return arr


# ── 2. Y-Eksenine Göre Satır Birleştirme (Spatial Alignment) ─────────────────
def _merge_boxes_into_lines(
    ocr_results: list,
    y_tolerance: int = _LINE_Y_TOLERANCE,
) -> List[Tuple[str, float]]:
    """
    EasyOCR'ın (bbox, text, confidence) çıktısını Y koordinatına göre
    satırlara gruplar ve her satırdaki kelimeleri soldan sağa birleştirir.

    Algoritma:
      1. Her tespit için *orta Y* = (üst-sol Y + alt-sol Y) / 2  hesapla.
      2. Tespitleri orta-Y'ye göre sırala.
      3. Ardışık tespitler arasındaki Y farkı ≤ y_tolerance ise aynı satır.
      4. Her satır içinde kelimeleri X'e göre sırala ve boşlukla birleştir.

    Args:
        ocr_results: EasyOCR readtext(detail=1) çıktısı.
                     Her eleman: (bbox, text, confidence)
                     bbox = [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
        y_tolerance: Aynı satır kabul edilecek max Y farkı (px).

    Returns:
        [(line_text, avg_confidence), ...] satır sırasıyla.
    """
    if not ocr_results:
        return []

    # Her tespit için (mid_y, min_x, text, confidence) oluştur
    items = []
    for bbox, text, conf in ocr_results:
        text = text.strip()
        if not text:
            continue
        # bbox köşeleri: [üst-sol, üst-sağ, alt-sağ, alt-sol]
        ys = [pt[1] for pt in bbox]
        xs = [pt[0] for pt in bbox]
        mid_y = (min(ys) + max(ys)) / 2.0
        min_x = min(xs)
        items.append((mid_y, min_x, text, conf))

    if not items:
        return []

    # Orta-Y'ye göre sırala
    items.sort(key=lambda it: it[0])

    # Satırları grupla
    lines: List[List[Tuple[float, float, str, float]]] = []
    current_line: List[Tuple[float, float, str, float]] = [items[0]]
    current_y = items[0][0]

    for item in items[1:]:
        if abs(item[0] - current_y) <= y_tolerance:
            # Aynı satır
            current_line.append(item)
        else:
            # Yeni satır başlat
            lines.append(current_line)
            current_line = [item]
            current_y = item[0]
    lines.append(current_line)  # son satırı ekle

    # Her satırı X'e göre sırala ve birleştir
    merged: List[Tuple[str, float]] = []
    for line_items in lines:
        line_items.sort(key=lambda it: it[1])  # min_x'e göre sırala
        line_text = " ".join(it[2] for it in line_items)
        avg_conf = sum(it[3] for it in line_items) / len(line_items)
        merged.append((line_text, avg_conf))

    return merged


# ── 3. Ana Fonksiyon ─────────────────────────────────────────────────────────
def extract_text(image_bytes: bytes) -> Tuple[str, float]:
    """
    Fiş görselinden metin çıkarır.

    Pipeline:
      1. Boyut & format doğrulama
      2. Görüntü ön işleme (grayscale, kontrast, keskinlik)
      3. EasyOCR ile metin tespiti (detail=1 → bbox dahil)
      4. Y-eksenine göre satır birleştirme
      5. Satır satır düzgün metin döndürme

    Args:
        image_bytes: JPEG/PNG görsel bytes (max 5 MB).

    Returns:
        (raw_text, confidence_0_to_100)
        raw_text: Satır satır birleştirilmiş metin.

    Raises:
        ValueError: Görsel boyutu > 5 MB veya boş.
        ReceiptProcessingError: OCR başarısız veya metin çıkarılamadı.
    """
    if len(image_bytes) > MAX_IMAGE_SIZE_BYTES:
        raise ValueError(
            f"Görsel 5MB'dan büyük olamaz ({len(image_bytes) / 1024 / 1024:.1f}MB)"
        )
    if len(image_bytes) == 0:
        raise ValueError("Boş görsel")

    # ── Ön İşleme ────────────────────────────────────────────────────────────
    try:
        img_array = _preprocess_image(image_bytes)
    except ReceiptProcessingError:
        raise
    except Exception as e:
        logger.exception("Preprocessing error: %s", e)
        raise ReceiptProcessingError(
            "Fiş okunamadı veya restoran tespit edilemedi, lütfen daha net bir görüntü yükleyin",
            "OCR_UNREADABLE",
        )

    # ── OCR (detail=1 → bbox + text + confidence) ────────────────────────────
    try:
        reader = _get_reader()
        ocr_results = reader.readtext(img_array, detail=1)
    except ReceiptProcessingError:
        raise
    except Exception as e:
        logger.exception("OCR extraction error: %s", e)
        raise ReceiptProcessingError(
            "Fiş okunamadı veya restoran tespit edilemedi, lütfen daha net bir görüntü yükleyin",
            "OCR_UNREADABLE",
        )

    # ── Satır Birleştirme ─────────────────────────────────────────────────────
    merged_lines = _merge_boxes_into_lines(ocr_results)

    if not merged_lines:
        raise ReceiptProcessingError(
            "Fiş okunamadı veya restoran tespit edilemedi, lütfen daha net bir görüntü yükleyin",
            "OCR_UNREADABLE",
        )

    raw_text = "\n".join(line_text for line_text, _ in merged_lines)
    avg_confidence = (
        sum(conf for _, conf in merged_lines) / len(merged_lines) * 100
    )

    logger.info(
        "OCR completed: %d lines, avg_confidence=%.1f%%, text_length=%d",
        len(merged_lines), avg_confidence, len(raw_text),
    )
    return raw_text, round(avg_confidence, 2)


# ── Singleton Facade ──────────────────────────────────────────────────────────
class OCRService:
    """OCR service facade for dependency injection."""

    def extract(self, image_bytes: bytes) -> Tuple[str, float]:
        return extract_text(image_bytes)


ocr_service = OCRService()
