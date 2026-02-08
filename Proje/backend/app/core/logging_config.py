"""
Logging Configuration - Loguru (TASK-BE-019)
Structured logging, rotation, console/file
"""
import logging
import sys
from pathlib import Path

from loguru import logger

from app.core.config import settings

# Log seviyeleri
LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR")
LOG_LEVEL = settings.LOG_LEVEL.upper() if settings.LOG_LEVEL.upper() in LOG_LEVELS else "INFO"

# Log dosyası (production)
LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "app.log"
LOG_MAX_SIZE = "100 MB"
LOG_RETENTION = "7 days"


class InterceptHandler(logging.Handler):
    """Standard logging'i Loguru'ya yönlendirir."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())


def setup_logging() -> None:
    """Loguru yapılandırması. Startup'ta çağrılır."""
    # Varsayılan handler'ı kaldır
    logger.remove()

    # 1. Console - Development: renkli, okunabilir
    logger.add(
        sys.stderr,
        level=LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
    )

    # 2. File - Production: JSON structured, rotation
    if settings.ENVIRONMENT != "development" or not settings.DEBUG:
        LOG_DIR.mkdir(exist_ok=True)
        logger.add(
            str(LOG_FILE),
            level=LOG_LEVEL,
            serialize=True,  # JSON format
            rotation=LOG_MAX_SIZE,
            retention=LOG_RETENTION,
            compression="gz",
        )

    # 3. Standard logging (logging.getLogger) -> Loguru
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    for name in ("uvicorn", "uvicorn.error", "sqlalchemy"):
        logging.getLogger(name).handlers = [InterceptHandler()]


def bind_user_context(user_id: str | None = None, role: str | None = None) -> None:
    """Request loglarına user context ekler."""
    if user_id:
        logger.configure(extra={"user_id": str(user_id), "role": role or ""})
