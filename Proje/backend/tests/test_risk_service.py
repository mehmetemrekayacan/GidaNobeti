"""
TASK-QA-001: Risk Service Unit Tests
update_restaurant_risk_status algoritması - DB gerekir (Docker ile çalışır).
"""
import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.db.models.dormitory import Dormitory
from app.db.models.user import User, UserRole
from app.db.models.restaurant import Restaurant, RiskStatus
from app.db.models.order import Order, EntryMethod
from app.db.models.incident import HealthIncident
from app.services.risk_service import update_restaurant_risk_status


@pytest.fixture
async def db_session():
    """Async DB session - test için."""
    async with AsyncSessionLocal() as session:
        yield session


@pytest.fixture
async def test_dorm(db_session: AsyncSession):
    """Test yurdu."""
    dorm = Dormitory(name="Test Yurt", city="TestCity", is_active=True)
    db_session.add(dorm)
    await db_session.flush()
    yield dorm
    await db_session.rollback()


@pytest.fixture
async def test_user(db_session: AsyncSession, test_dorm):
    """Test kullanıcı (öğrenci)."""
    from app.core.security import hash_password
    user = User(
        tckn_hash="test_hash_risk_123",
        full_name="Test Öğrenci",
        password_hash=hash_password("Test123!"),
        role=UserRole.STUDENT,
        dorm_id=test_dorm.id,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.flush()
    yield user
    # rollback conftest'te

@pytest.fixture
async def test_restaurant(db_session: AsyncSession):
    """Test restoran."""
    rest = Restaurant(
        name="Test Restoran",
        normalized_name="TEST RESTORAN",
        current_risk_status=RiskStatus.SAFE,
        total_orders=100,
        total_complaints=0,
        is_active=True,
    )
    db_session.add(rest)
    await db_session.flush()
    yield rest
    await db_session.rollback()


@pytest.mark.asyncio
class TestRiskService:
    """update_restaurant_risk_status testleri."""

    async def test_safe_restaurant_stays_safe(self, db_session, test_restaurant):
        """Şikayet yoksa SAFE kalır."""
        await update_restaurant_risk_status(db_session, test_restaurant.id)
        await db_session.refresh(test_restaurant)
        assert test_restaurant.current_risk_status == RiskStatus.SAFE

    async def test_red_flag_on_three_incidents(
        self, db_session, test_restaurant, test_user
    ):
        """Son 24 saatte 3+ şikayet → RED_FLAG."""
        # Order oluştur
        order = Order(
            user_id=test_user.id,
            restaurant_id=test_restaurant.id,
            method=EntryMethod.MANUAL_ENTRY,
        )
        db_session.add(order)
        await db_session.flush()

        # 3 incident ekle
        now = datetime.now(timezone.utc)
        for _ in range(3):
            inc = HealthIncident(
                user_id=test_user.id,
                suspected_order_id=order.id,
                symptoms="Test semptom",
                report_date=now,
            )
            db_session.add(inc)
        await db_session.flush()

        test_restaurant.total_complaints = 3
        await db_session.flush()

        await update_restaurant_risk_status(db_session, test_restaurant.id)
        await db_session.refresh(test_restaurant)
        assert test_restaurant.current_risk_status == RiskStatus.RED_FLAG

    async def test_watchlist_on_two_incidents(
        self, db_session, test_restaurant, test_user
    ):
        """Son 24 saatte 2 şikayet → WATCHLIST."""
        order = Order(
            user_id=test_user.id,
            restaurant_id=test_restaurant.id,
            method=EntryMethod.MANUAL_ENTRY,
        )
        db_session.add(order)
        await db_session.flush()

        now = datetime.now(timezone.utc)
        for _ in range(2):
            inc = HealthIncident(
                user_id=test_user.id,
                suspected_order_id=order.id,
                symptoms="Bulgular",
                report_date=now,
            )
            db_session.add(inc)
        await db_session.flush()
        test_restaurant.total_complaints = 2
        await db_session.flush()

        await update_restaurant_risk_status(db_session, test_restaurant.id)
        await db_session.refresh(test_restaurant)
        assert test_restaurant.current_risk_status == RiskStatus.WATCHLIST
