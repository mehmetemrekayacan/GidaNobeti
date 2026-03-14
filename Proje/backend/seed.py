"""Comprehensive idempotent seed script for local/dev environments."""

import asyncio
import os
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy import select

# Add backend root to path so `app.*` imports work when script is run directly.
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.core.security import hash_password, hash_tckn
from app.db.models.dormitory import Dormitory
from app.db.models.incident import HealthIncident, ReportStatus
from app.db.models.order import EntryMethod, Order
from app.db.models.restaurant import Restaurant, RiskStatus
from app.db.models.user import User, UserRole
from app.db.session import AsyncSessionLocal


def _load_env_file(env_path: Path) -> dict[str, str]:
    """Minimal .env parser (KEY=VALUE) for local script runs."""
    data: dict[str, str] = {}
    if not env_path.exists():
        return data

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        data[key] = value
    return data


ENV_FILE_VALUES = _load_env_file(Path(__file__).resolve().parent.parent / ".env")


def _get_env(name: str, default: str | None = None) -> str | None:
    """Resolve value from process env, settings (if available), then .env file fallback."""
    value = os.getenv(name)
    if value is not None and value != "":
        return value

    settings_value = getattr(settings, name, None)
    if isinstance(settings_value, str) and settings_value != "":
        return settings_value

    return ENV_FILE_VALUES.get(name, default)


def _resolve_role(role_name: str | None, default_role: UserRole) -> UserRole:
    if not role_name:
        return default_role
    try:
        return UserRole(role_name)
    except ValueError:
        print(f"[seed] Invalid role '{role_name}', using default '{default_role.value}'.")
        return default_role


def _normalize_name(value: str) -> str:
    replacements = str.maketrans({
        "ı": "i",
        "İ": "I",
        "ğ": "g",
        "Ğ": "G",
        "ü": "u",
        "Ü": "U",
        "ş": "s",
        "Ş": "S",
        "ö": "o",
        "Ö": "O",
        "ç": "c",
        "Ç": "C",
    })
    return value.translate(replacements).upper()


async def _seed_dormitories() -> dict[str, Dormitory]:
    dorms = [
        {
            "name": "Zeki Muren KYK Yurdu",
            "city": "Isparta",
            "district": "Merkez",
            "address": "Pirimehmet Mah. 1742 Sok. No:5",
            "capacity": 1800,
            "phone": "02462110001",
            "latitude": 37.7665,
            "longitude": 30.5532,
        },
        {
            "name": "Ataturk KYK Yurdu",
            "city": "Isparta",
            "district": "Merkez",
            "address": "Cunur Mah. 220 Cad. No:14",
            "capacity": 2200,
            "phone": "02462110002",
            "latitude": 37.7801,
            "longitude": 30.5410,
        },
        {
            "name": "Mimar Sinan KYK Yurdu",
            "city": "Isparta",
            "district": "Merkez",
            "address": "Fatih Mah. 101 Cad. No:20",
            "capacity": 1600,
            "phone": "02462110003",
            "latitude": 37.7739,
            "longitude": 30.5478,
        },
    ]

    seeded: dict[str, Dormitory] = {}
    async with AsyncSessionLocal() as db:
        for item in dorms:
            stmt = select(Dormitory).where(Dormitory.name == item["name"])
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing:
                seeded[item["name"]] = existing
                print(f"[seed] Dormitory already exists: {item['name']}")
                continue

            dorm = Dormitory(
                name=item["name"],
                city=item["city"],
                district=item["district"],
                address=item["address"],
                capacity=item["capacity"],
                phone=item["phone"],
                latitude=item["latitude"],
                longitude=item["longitude"],
                is_active=True,
            )
            db.add(dorm)
            await db.flush()
            seeded[item["name"]] = dorm
            print(f"[seed] Dormitory created: {item['name']}")

        await db.commit()

    return seeded


async def _seed_restaurants() -> dict[str, Restaurant]:
    restaurants = [
        {
            "name": "Anadolu Sofrasi",
            "district": "Merkez",
            "address": "Kutlubey Mah. 1106 Sok. No:8",
            "platform_origin": "Yemeksepeti",
            "risk": RiskStatus.SAFE,
            "risk_reason": None,
            "total_complaints": 0,
            "total_orders": 240,
            "avg_rating": 4.7,
            "lat": 37.7642,
            "lng": 30.5520,
        },
        {
            "name": "Campus Doner",
            "district": "Merkez",
            "address": "Cunur Mah. 102 Cad. No:31",
            "platform_origin": "Trendyol",
            "risk": RiskStatus.WATCHLIST,
            "risk_reason": "Son 30 gunde artan mide bulantisi sikayetleri",
            "total_complaints": 3,
            "total_orders": 198,
            "avg_rating": 4.0,
            "lat": 37.7791,
            "lng": 30.5395,
        },
        {
            "name": "Lezzet Duragi",
            "district": "Merkez",
            "address": "Modernevler Mah. 142 Cad. No:3",
            "platform_origin": "Getir",
            "risk": RiskStatus.BLACKLISTED,
            "risk_reason": "Dogrulanmis gida zehirlenmesi vakalari",
            "total_complaints": 7,
            "total_orders": 112,
            "avg_rating": 2.9,
            "lat": 37.7710,
            "lng": 30.5455,
        },
        {
            "name": "Gul Kebap Salonu",
            "district": "Merkez",
            "address": "Sanayi Mah. 3209 Sok. No:11",
            "platform_origin": "Yemeksepeti",
            "risk": RiskStatus.SAFE,
            "risk_reason": None,
            "total_complaints": 1,
            "total_orders": 305,
            "avg_rating": 4.5,
            "lat": 37.7578,
            "lng": 30.5608,
        },
        {
            "name": "Ege Fast Food",
            "district": "Merkez",
            "address": "Bahcelievler Mah. 108 Cad. No:27",
            "platform_origin": "Trendyol",
            "risk": RiskStatus.WATCHLIST,
            "risk_reason": "Hijyen denetiminde iyilestirme uyarisi",
            "total_complaints": 2,
            "total_orders": 176,
            "avg_rating": 3.8,
            "lat": 37.7688,
            "lng": 30.5482,
        },
    ]

    seeded: dict[str, Restaurant] = {}
    now = datetime.utcnow()
    async with AsyncSessionLocal() as db:
        for item in restaurants:
            stmt = select(Restaurant).where(Restaurant.name == item["name"])
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing:
                seeded[item["name"]] = existing
                print(f"[seed] Restaurant already exists: {item['name']}")
                continue

            restaurant = Restaurant(
                name=item["name"],
                normalized_name=_normalize_name(item["name"]),
                district=item["district"],
                address=item["address"],
                platform_origin=item["platform_origin"],
                current_risk_status=item["risk"],
                risk_updated_at=now,
                risk_reason=item["risk_reason"],
                total_complaints=item["total_complaints"],
                total_orders=item["total_orders"],
                avg_rating=item["avg_rating"],
                latitude=item["lat"],
                longitude=item["lng"],
                is_active=True,
            )
            db.add(restaurant)
            await db.flush()
            seeded[item["name"]] = restaurant
            print(f"[seed] Restaurant created: {item['name']}")

        await db.commit()

    return seeded


async def _create_or_update_user(
    *,
    tckn: str,
    password: str,
    full_name: str,
    role: UserRole,
    dorm_id: int | None,
    email: str | None,
    phone_number: str | None,
    room_number: str | None,
) -> User:
    tckn_hash_value = hash_tckn(tckn)

    async with AsyncSessionLocal() as db:
        stmt = select(User).where(User.tckn_hash == tckn_hash_value)
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            changed = False
            if existing.full_name != full_name:
                existing.full_name = full_name
                changed = True
            if existing.role != role:
                existing.role = role
                changed = True
            if existing.dorm_id != dorm_id:
                existing.dorm_id = dorm_id
                changed = True
            if email and existing.email != email:
                existing.email = email
                changed = True
            if phone_number and existing.phone_number != phone_number:
                existing.phone_number = phone_number
                changed = True
            if room_number and existing.room_number != room_number:
                existing.room_number = room_number
                changed = True
            if not existing.is_active:
                existing.is_active = True
                changed = True
            if not existing.is_verified:
                existing.is_verified = True
                changed = True

            if changed:
                await db.commit()
                print(f"[seed] User updated: {full_name}")
            else:
                print(f"[seed] User already exists: {full_name}")

            await db.refresh(existing)
            return existing

        user = User(
            dorm_id=dorm_id,
            tckn_hash=tckn_hash_value,
            password_hash=hash_password(password),
            full_name=full_name,
            email=email,
            phone_number=phone_number,
            room_number=room_number,
            role=role,
            is_active=True,
            is_verified=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        print(f"[seed] User created: {full_name}")
        return user


async def _seed_users(dorms: dict[str, Dormitory]) -> dict[str, User]:
    admin_tckn = _get_env("SEED_ADMIN_TCKN", "11111111111")
    admin_password = _get_env("SEED_ADMIN_PASSWORD", "Admin123!")
    student_tckn = _get_env("SEED_STUDENT_TCKN", "12345678901")
    student_password = _get_env("SEED_STUDENT_PASSWORD", "Test123!")

    if not admin_tckn or not admin_password:
        raise RuntimeError("SEED_ADMIN_TCKN and SEED_ADMIN_PASSWORD must be set.")
    if not student_tckn or not student_password:
        raise RuntimeError("SEED_STUDENT_TCKN and SEED_STUDENT_PASSWORD must be set.")

    admin_role = _resolve_role(_get_env("SEED_ADMIN_ROLE"), UserRole.SYS_ADMIN)
    student_role = _resolve_role(_get_env("SEED_STUDENT_ROLE"), UserRole.STUDENT)

    dorm_cycle = list(dorms.values())
    if not dorm_cycle:
        raise RuntimeError("No dormitory found for seeding users.")

    users_by_label: dict[str, User] = {}

    users_by_label["admin"] = await _create_or_update_user(
        tckn=admin_tckn,
        password=admin_password,
        full_name=_get_env("SEED_ADMIN_FULL_NAME", "System Admin") or "System Admin",
        role=admin_role,
        dorm_id=dorm_cycle[0].id,
        email=_get_env("SEED_ADMIN_EMAIL", "admin@gidanobeti.local"),
        phone_number=_get_env("SEED_ADMIN_PHONE", "05550000001"),
        room_number=None,
    )

    student_blueprint = [
        {
            "label": "student_primary",
            "tckn": student_tckn,
            "password": student_password,
            "full_name": _get_env("SEED_STUDENT_FULL_NAME", "Test Student") or "Test Student",
            "email": _get_env("SEED_STUDENT_EMAIL", "test.student@gidanobeti.local"),
            "phone": _get_env("SEED_STUDENT_PHONE", "05550000011"),
            "room": _get_env("SEED_STUDENT_ROOM", "A-101"),
        },
        {
            "label": "student_2",
            "tckn": "12345678902",
            "password": "Test123!",
            "full_name": "Ayse Demir",
            "email": "ayse.demir@gidanobeti.local",
            "phone": "05550000012",
            "room": "B-203",
        },
        {
            "label": "student_3",
            "tckn": "12345678903",
            "password": "Test123!",
            "full_name": "Mehmet Kaya",
            "email": "mehmet.kaya@gidanobeti.local",
            "phone": "05550000013",
            "room": "C-307",
        },
        {
            "label": "student_4",
            "tckn": "12345678904",
            "password": "Test123!",
            "full_name": "Elif Aydin",
            "email": "elif.aydin@gidanobeti.local",
            "phone": "05550000014",
            "room": "D-115",
        },
    ]

    for index, item in enumerate(student_blueprint):
        dorm_id = dorm_cycle[index % len(dorm_cycle)].id
        users_by_label[item["label"]] = await _create_or_update_user(
            tckn=item["tckn"],
            password=item["password"],
            full_name=item["full_name"],
            role=student_role,
            dorm_id=dorm_id,
            email=item["email"],
            phone_number=item["phone"],
            room_number=item["room"],
        )

    return users_by_label


def _build_order_seed_plan(
    students: dict[str, User],
    restaurants: dict[str, Restaurant],
) -> list[dict[str, object]]:
    rng = random.Random(20260314)
    student_keys = [
        "student_primary",
        "student_2",
        "student_3",
        "student_4",
    ]
    restaurant_names = list(restaurants.keys())
    food_pool = [
        "Tavuk doner + ayran",
        "Karisik pizza + kola",
        "Mercimek corbasi + pilav",
        "Hamburger menu",
        "Tavuklu salata + su",
        "Lahmacun + ayran",
    ]
    base = datetime.utcnow() - timedelta(days=35)

    plan: list[dict[str, object]] = []
    for i in range(12):
        student_label = student_keys[i % len(student_keys)]
        restaurant_name = restaurant_names[rng.randint(0, len(restaurant_names) - 1)]
        days_offset = rng.randint(1, 33)
        minute_offset = rng.randint(0, 23 * 60)
        declared_at = base + timedelta(days=days_offset, minutes=minute_offset)
        total_amount = round(rng.uniform(85, 360), 2)

        plan.append(
            {
                "seed_key": f"SEED:ORDER:{i + 1:03d}",
                "student_id": students[student_label].id,
                "restaurant_id": restaurants[restaurant_name].id,
                "declared_at": declared_at,
                "receipt_date": declared_at - timedelta(minutes=rng.randint(10, 90)),
                "total_amount": total_amount,
                "food_content": food_pool[rng.randint(0, len(food_pool) - 1)],
                "verified": rng.choice([True, True, False]),
                "method": EntryMethod.MANUAL_ENTRY,
            }
        )

    return plan


async def _seed_orders(
    students: dict[str, User],
    restaurants: dict[str, Restaurant],
) -> dict[str, Order]:
    plan = _build_order_seed_plan(students, restaurants)
    seeded: dict[str, Order] = {}

    async with AsyncSessionLocal() as db:
        for item in plan:
            seed_key = str(item["seed_key"])
            stmt = select(Order).where(Order.manual_note == seed_key)
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                seeded[seed_key] = existing
                print(f"[seed] Order already exists: {seed_key}")
                continue

            order = Order(
                user_id=item["student_id"],
                restaurant_id=item["restaurant_id"],
                declared_at=item["declared_at"],
                receipt_date=item["receipt_date"],
                method=item["method"],
                manual_note=seed_key,
                total_amount=item["total_amount"],
                food_content=item["food_content"],
                is_verified=bool(item["verified"]),
                verification_notes="Seed generated historical order",
            )
            db.add(order)
            await db.flush()
            seeded[seed_key] = order
            print(f"[seed] Order created: {seed_key}")

        await db.commit()

    return seeded


async def _seed_incidents(
    students: dict[str, User],
    orders: dict[str, Order],
) -> None:
    incident_plan = [
        {
            "seed_key": "SEED:INCIDENT:001",
            "student_label": "student_primary",
            "order_key": "SEED:ORDER:002",
            "symptoms": "Gida zehirlenmesi: mide bulantisi, kusma, karin agrisi",
            "severity": 4,
            "status": ReportStatus.CONFIRMED,
            "hospital": "Isparta Sehir Hastanesi",
        },
        {
            "seed_key": "SEED:INCIDENT:002",
            "student_label": "student_2",
            "order_key": "SEED:ORDER:007",
            "symptoms": "Hijyen sorunu supheli: karin agrisi ve hafif ates",
            "severity": 3,
            "status": ReportStatus.INVESTIGATING,
            "hospital": "Suleyman Demirel Universitesi Hastanesi",
        },
        {
            "seed_key": "SEED:INCIDENT:003",
            "student_label": "student_4",
            "order_key": "SEED:ORDER:010",
            "symptoms": "Gida zehirlenmesi: siddetli ishal ve halsizlik",
            "severity": 5,
            "status": ReportStatus.PENDING,
            "hospital": "Isparta Devlet Hastanesi",
        },
    ]

    async with AsyncSessionLocal() as db:
        for item in incident_plan:
            seed_key = item["seed_key"]
            stmt = select(HealthIncident).where(HealthIncident.admin_notes == seed_key)
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing:
                print(f"[seed] Incident already exists: {seed_key}")
                continue

            related_order = orders.get(item["order_key"])
            student = students[item["student_label"]]
            symptom_start = datetime.utcnow() - timedelta(days=2, hours=6)

            incident = HealthIncident(
                user_id=student.id,
                suspected_order_id=related_order.id if related_order else None,
                symptoms=item["symptoms"],
                symptom_start_time=symptom_start,
                severity_level=item["severity"],
                is_verified_by_doctor=item["status"] == ReportStatus.CONFIRMED,
                doctor_name="Dr. Selin Aksoy" if item["status"] == ReportStatus.CONFIRMED else None,
                doctor_notes="Gida kaynakli suphe mevcut" if item["status"] == ReportStatus.CONFIRMED else None,
                hospital_name=item["hospital"],
                report_date=datetime.utcnow() - timedelta(days=1),
                status=item["status"],
                admin_notes=seed_key,
            )
            db.add(incident)
            print(f"[seed] Incident created: {seed_key}")

        await db.commit()


async def seed_all() -> None:
    print("[seed] Starting comprehensive seed process...")
    dorms = await _seed_dormitories()
    restaurants = await _seed_restaurants()
    users = await _seed_users(dorms)

    student_users = {
        key: value
        for key, value in users.items()
        if value.role == UserRole.STUDENT
    }

    orders = await _seed_orders(student_users, restaurants)
    await _seed_incidents(student_users, orders)

    print("[seed] Seed process completed successfully.")


async def main() -> None:
    await seed_all()


if __name__ == "__main__":
    asyncio.run(main())