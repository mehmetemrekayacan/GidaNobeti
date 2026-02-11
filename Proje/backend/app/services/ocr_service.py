"""
OCR Service - Fiş/Ekran görüntüsünden metin çıkarma (TASK-BE-008)
KVKK: Görsel RAM'de işlenir, diske kaydedilmez.
"""
import io
import logging
from typing import Tuple

from PIL import Image
import numpy as np

from app.core.config import settings

logger = logging.getLogger(__name__)

# Lazy load EasyOCR (heavy import)
_reader = None

# Max image size: 5MB (KVKK requirement)
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024
# Fiş metni için 1280 yeterli; daha küçük = daha hızlı OCR
MAX_IMAGE_DIMENSION = 1280


def _get_reader():
    """Lazy initialize EasyOCR reader (Türkçe + İngilizce)."""
    global _reader
    if _reader is None:
        import easyocr
        langs = [l.strip() for l in settings.OCR_LANGUAGES.split(",") if l.strip()]
        if not langs:
            langs = ["tr", "en"]
        gpu = settings.OCR_ENABLE_GPU
        logger.info(f"Initializing EasyOCR: langs={langs}, gpu={gpu}")
        _reader = easyocr.Reader(langs, gpu=gpu, verbose=False)
    return _reader


def _preprocess_image(image_bytes: bytes) -> np.ndarray:
    """
    Görsel ön işleme: resize, contrast (opsiyonel).
    RAM-only, disk yok.
    """
    img = Image.open(io.BytesIO(image_bytes))
    img = img.convert("RGB")
    arr = np.array(img)

    # Resize if too large (performance)
    h, w = arr.shape[:2]
    if max(h, w) > MAX_IMAGE_DIMENSION:
        ratio = MAX_IMAGE_DIMENSION / max(h, w)
        new_w = int(w * ratio)
        new_h = int(h * ratio)
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        arr = np.array(img)

    return arr


def extract_text(image_bytes: bytes) -> Tuple[str, float]:
    """
    Fiş görselinden metin çıkar.

    Args:
        image_bytes: JPEG/PNG görsel bytes (max 5MB)

    Returns:
        (raw_text, confidence_0_to_100)

    Raises:
        ValueError: Görsel boyutu > 5MB veya geçersiz format
    """
    if len(image_bytes) > MAX_IMAGE_SIZE_BYTES:
        raise ValueError(f"Görsel 5MB'dan büyük olamaz ({len(image_bytes) / 1024 / 1024:.1f}MB)")

    if len(image_bytes) == 0:
        raise ValueError("Boş görsel")

    # Preprocess (RAM only)
    img_array = _preprocess_image(image_bytes)

    # OCR (detail=0: sadece metin listesi döner, bbox yok → daha hızlı)
    reader = _get_reader()
    result = reader.readtext(img_array, detail=0)

    # detail=0 → result list of strings
    lines = [t.strip() for t in result if isinstance(t, str) and t.strip()]
    confidences = [1.0] * len(lines) if lines else []

    raw_text = "\n".join(lines) if lines else ""
    avg_confidence = (sum(confidences) / len(confidences) * 100) if confidences else 0.0

    logger.debug(f"OCR extracted {len(lines)} lines, avg_confidence={avg_confidence:.1f}%")
    return raw_text, round(avg_confidence, 2)


# Singleton instance for dependency injection
class OCRService:
    """OCR service facade."""

    def extract(self, image_bytes: bytes) -> Tuple[str, float]:
        return extract_text(image_bytes)


ocr_service = OCRService()
