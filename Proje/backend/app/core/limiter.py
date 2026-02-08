"""
Rate Limiting - Redis-backed (TASK-BE-018)
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

# Redis storage - limits paketi redis:// formatını destekler
# headers_enabled=False: FastAPI Pydantic response ile uyumluluk (response objesi gerekir)
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.REDIS_URL,
    default_limits=["100/minute"],  # Global: 100 req/min per IP
    application_limits=["100/minute"],
    headers_enabled=False,  # FastAPI JSON response ile çakışma önlenir
    swallow_errors=False,
    in_memory_fallback_enabled=True,  # Redis down ise in-memory fallback
)
