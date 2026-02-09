"""
Test fixtures - TASK-QA-001
Test client, DB session override, mock data.
"""
import asyncio
import os
import pytest
from httpx import ASGITransport, AsyncClient

# Test ortamı - REDIS/DATABASE yoksa bazı testler skip
os.environ.setdefault("TESTING", "1")

# Event loop - tüm async testler aynı loop'ta (event_loop conflict önleme)
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def async_client():
    """Async HTTP client - FastAPI app'e karşı."""
    from app.main import app
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        timeout=30.0,
    ) as client:
        yield client


@pytest.fixture
def sample_receipt_text():
    """Örnek fiş metni - parser testleri için (total toplam satırı önce gelmeli)."""
    return """
PASAPORT PIZZA
Merkez, Isparta
Sipariş No: 12345
Toplam: 115.00 TL
---
2x Karışık Pizza    85.00 TL
1x Kola 330ml       15.00 TL
---
21.01.2026 19:30
"""
