"""
TASK-QA-001: API Integration Tests
Health, Auth endpoint'leri - DB/Redis gerektirir (Docker ile çalışır).
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestHealthEndpoint:
    """Health check endpoint testleri."""

    async def test_health_returns_200(self, async_client: AsyncClient):
        """GET /health 200 döner."""
        response = await async_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data

    async def test_root_returns_api_info(self, async_client: AsyncClient):
        """GET / 200 ve API bilgisi döner."""
        response = await async_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data


@pytest.mark.asyncio
class TestAuthEndpoint:
    """Auth endpoint testleri - seed data ile test."""

    async def test_login_success_with_seed_user(self, async_client: AsyncClient):
        """Seed'deki admin ile login başarılı."""
        response = await async_client.post(
            "/v1/auth/login",
            json={"tckn": "11111111111", "password": "Admin123!"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data

    async def test_login_fail_wrong_password(self, async_client: AsyncClient):
        """Yanlış şifre ile 401."""
        response = await async_client.post(
            "/v1/auth/login",
            json={"tckn": "11111111111", "password": "WrongPassword123!"},
        )
        assert response.status_code == 401

    async def test_login_fail_invalid_tckn(self, async_client: AsyncClient):
        """Geçersiz TCKN formatı ile 422."""
        response = await async_client.post(
            "/v1/auth/login",
            json={"tckn": "123", "password": "Test123!"},
        )
        assert response.status_code == 422


@pytest.mark.asyncio
class TestAdminIncidentsEndpoint:
    """Admin incidents endpoint testleri."""

    async def test_admin_incidents_list_requires_auth(self, async_client: AsyncClient):
        """GET /admin/incidents auth gerektirir."""
        response = await async_client.get("/v1/admin/incidents")
        assert response.status_code == 401  # No Bearer token

    async def test_admin_incidents_list_with_auth(self, async_client: AsyncClient):
        """Admin token ile incidents listesi döner."""
        login_resp = await async_client.post(
            "/v1/auth/login",
            json={"tckn": "11111111111", "password": "Admin123!"},
        )
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]

        response = await async_client.get(
            "/v1/admin/incidents",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data
        assert isinstance(data["items"], list)
