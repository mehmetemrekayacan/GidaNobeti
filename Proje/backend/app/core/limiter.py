"""
Rate Limiting - Redis-backed (TASK-BE-018)
"""
import uuid
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings


def _limiter_key_func(request):
    """Test modunda her istek için benzersiz key (rate limit bypass)."""
    if settings.TESTING:
        return str(uuid.uuid4())
    return get_remote_address(request)


# Redis storage - limits paketi redis:// formatını destekler
# headers_enabled=False: FastAPI Pydantic response ile uyumluluk (response objesi gerekir)
limiter = Limiter(
    key_func=_limiter_key_func,
    storage_uri=settings.REDIS_URL,
    default_limits=["100/minute"],  # Global: 100 req/min per IP
    application_limits=["100/minute"],
    headers_enabled=False,  # FastAPI JSON response ile çakışma önlenir
    swallow_errors=False,
    in_memory_fallback_enabled=True,  # Redis down ise in-memory fallback
)
