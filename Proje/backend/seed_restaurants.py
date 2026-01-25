"""
Seed script - Docker container içinde çalıştırılacak
"""
import asyncio
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.db.models.restaurant import Restaurant, RiskStatus
from app.db.models.user import User, UserRole
from app.db.models.dormitory import Dormitory
from app.core.security import hash_tckn, hash_password, verify_password


async def seed_dormitories():
    """Add test dormitory"""
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select, func
        count_query = select(func.count(Dormitory.id))
        result = await db.execute(count_query)
        count = result.scalar()
        
        if count > 0:
            print(f"✅ {count} dormitories already exist, skipping seed")
            dorm_query = select(Dormitory).limit(1)
            dorm_result = await db.execute(dorm_query)
            dorm = dorm_result.scalar_one()
            return dorm.id
        
        dormitory = Dormitory(
            name="Isparta Erkek KYK Yurdu",
            city="Isparta",
            district="Merkez",
            address="Test Adresi",
            capacity=2000,
            phone="02461234567",
            latitude=37.7749,
            longitude=30.5567,
            is_active=True
        )
        
        db.add(dormitory)
        await db.commit()
        await db.refresh(dormitory)
        print(f"✅ Seeded dormitory: {dormitory.name}")
        return dormitory.id


async def seed_users(dorm_id: int):
    """Add test users"""
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select, func
        
        # Check for admin user specifically
        admin_tckn_hash = hash_tckn("11111111111")
        admin_query = select(User).where(User.tckn_hash == admin_tckn_hash)
        admin_result = await db.execute(admin_query)
        existing_admin = admin_result.scalar_one_or_none()
        
        if existing_admin:
            print(f"✅ Admin user already exists (TCKN: 11111111111)")
            # Verify password works
            password_updated = False
            if not verify_password("Admin123!", existing_admin.password_hash):
                print("   ⚠️ Admin password hash mismatch, updating...")
                existing_admin.password_hash = hash_password("Admin123!")
                password_updated = True
            
            # Ensure admin role is correct
            role_updated = False
            if existing_admin.role != UserRole.DORM_MANAGER:
                print(f"   ⚠️ Admin role is {existing_admin.role}, updating to DORM_MANAGER...")
                existing_admin.role = UserRole.DORM_MANAGER
                role_updated = True
            
            # Ensure account is active and verified
            if not existing_admin.is_active or not existing_admin.is_verified:
                existing_admin.is_active = True
                existing_admin.is_verified = True
                role_updated = True
            
            if password_updated or role_updated:
                await db.commit()
                if password_updated:
                    print("   ✅ Admin password updated")
                if role_updated:
                    print("   ✅ Admin role and status updated")
            else:
                print("   ✅ Admin password is correct")
                print("   ✅ Admin role is correct")
        else:
            print("   Creating admin user...")
            admin_user = User(
                dorm_id=dorm_id,
                tckn_hash=admin_tckn_hash,
                password_hash=hash_password("Admin123!"),
                full_name="Yurt Müdürü",
                email="mudur@test.com",
                phone_number="05551111111",
                role=UserRole.DORM_MANAGER,
                is_active=True,
                is_verified=True
            )
            db.add(admin_user)
            await db.commit()
            print("   ✅ Admin user created")
        
        # Check for student user
        student_tckn_hash = hash_tckn("12345678901")
        student_query = select(User).where(User.tckn_hash == student_tckn_hash)
        student_result = await db.execute(student_query)
        existing_student = student_result.scalar_one_or_none()
        
        if existing_student:
            print(f"✅ Student user already exists (TCKN: 12345678901)")
            password_updated = False
            if not verify_password("Test123!", existing_student.password_hash):
                print("   ⚠️ Student password hash mismatch, updating...")
                existing_student.password_hash = hash_password("Test123!")
                password_updated = True
            
            # Ensure account is active and verified
            status_updated = False
            if not existing_student.is_active or not existing_student.is_verified:
                existing_student.is_active = True
                existing_student.is_verified = True
                status_updated = True
            
            if password_updated or status_updated:
                await db.commit()
                if password_updated:
                    print("   ✅ Student password updated")
                if status_updated:
                    print("   ✅ Student account status updated")
            else:
                print("   ✅ Student password is correct")
                print("   ✅ Student account is active and verified")
        else:
            print("   Creating student user...")
            student_user = User(
                dorm_id=dorm_id,
                tckn_hash=student_tckn_hash,
                password_hash=hash_password("Test123!"),
                full_name="Ahmet Yılmaz",
                email="ahmet.yilmaz@test.com",
                phone_number="05551234567",
                room_number="A-205",
                role=UserRole.STUDENT,
                is_active=True,
                is_verified=True
            )
            db.add(student_user)
            await db.commit()
            print("   ✅ Student user created")
        
        print("\n📋 Test Kullanıcıları:")
        print("   Admin: TCKN=11111111111, Password=Admin123!")
        print("   Student: TCKN=12345678901, Password=Test123!")


async def seed_restaurants():
    """Add test restaurants to database"""
    async with AsyncSessionLocal() as db:
        # Check if restaurants already exist
        from sqlalchemy import select, func
        count_query = select(func.count(Restaurant.id))
        result = await db.execute(count_query)
        count = result.scalar()
        
        if count > 0:
            print(f"✅ {count} restaurants already exist, skipping seed")
            return
        
        restaurants = [
            Restaurant(
                name="Burger King Kadıköy",
                normalized_name="BURGER KING KADIKOY",
                district="Kadıköy",
                address="Rıhtım Cad. No:12/A",
                platform_origin="Trendyol",
                current_risk_status=RiskStatus.SAFE,
                total_complaints=0,
                total_orders=150,
                avg_rating=4.5,
                latitude=40.9886,
                longitude=29.0252,
                is_active=True
            ),
            Restaurant(
                name="McDonald's Beşiktaş",
                normalized_name="MCDONALD'S BESIKTAS",
                district="Beşiktaş",
                address="Barbaros Bulvarı No:45",
                platform_origin="Getir",
                current_risk_status=RiskStatus.SAFE,
                total_complaints=1,
                total_orders=320,
                avg_rating=4.7,
                latitude=41.0422,
                longitude=29.0070,
                is_active=True
            ),
            Restaurant(
                name="Domino's Pizza Şişli",
                normalized_name="DOMINO'S PIZZA SISLI",
                district="Şişli",
                address="Büyükdere Cad. No:100",
                platform_origin="Trendyol",
                current_risk_status=RiskStatus.SAFE,
                total_complaints=2,
                total_orders=280,
                avg_rating=4.3,
                latitude=41.0614,
                longitude=28.9865,
                is_active=True
            ),
            Restaurant(
                name="KFC Taksim",
                normalized_name="KFC TAKSIM",
                district="Beyoğlu",
                address="İstiklal Cad. No:200",
                platform_origin="Getir",
                current_risk_status=RiskStatus.WATCHLIST,
                risk_reason="3 şikayet alındı, takip ediliyor",
                total_complaints=3,
                total_orders=190,
                avg_rating=4.0,
                latitude=41.0370,
                longitude=28.9850,
                is_active=True
            ),
            Restaurant(
                name="Pizzeria Uno Üsküdar",
                normalized_name="PIZZERIA UNO USKUDAR",
                district="Üsküdar",
                address="Çavuşdere Cad. No:55",
                platform_origin="Trendyol",
                current_risk_status=RiskStatus.SAFE,
                total_complaints=0,
                total_orders=95,
                avg_rating=4.6,
                latitude=41.0225,
                longitude=29.0235,
                is_active=True
            ),
            Restaurant(
                name="Starbucks Zorlu Center",
                normalized_name="STARBUCKS ZORLU CENTER",
                district="Beşiktaş",
                address="Zorlu Center AVM",
                platform_origin="Getir",
                current_risk_status=RiskStatus.SAFE,
                total_complaints=0,
                total_orders=420,
                avg_rating=4.8,
                latitude=41.0677,
                longitude=29.0088,
                is_active=True
            ),
            Restaurant(
                name="Popeyes Levent",
                normalized_name="POPEYES LEVENT",
                district="Beşiktaş",
                address="Levent Mahallesi",
                platform_origin="Trendyol",
                current_risk_status=RiskStatus.SAFE,
                total_complaints=1,
                total_orders=175,
                avg_rating=4.4,
                latitude=41.0790,
                longitude=29.0066,
                is_active=True
            ),
            Restaurant(
                name="Arby's Maslak",
                normalized_name="ARBY'S MASLAK",
                district="Sarıyer",
                address="Maslak Meydan Sok.",
                platform_origin="Getir",
                current_risk_status=RiskStatus.RED_FLAG,
                risk_reason="5+ şikayet, gıda güvenliği inceleniyor",
                total_complaints=6,
                total_orders=210,
                avg_rating=3.5,
                latitude=41.1085,
                longitude=29.0229,
                is_active=True
            ),
            Restaurant(
                name="Sbarro Kanyon AVM",
                normalized_name="SBARRO KANYON AVM",
                district="Beşiktaş",
                address="Kanyon Alışveriş Merkezi",
                platform_origin="Trendyol",
                current_risk_status=RiskStatus.SAFE,
                total_complaints=0,
                total_orders=130,
                avg_rating=4.5,
                latitude=41.0815,
                longitude=29.0095,
                is_active=True
            ),
            Restaurant(
                name="Subway Bakırköy",
                normalized_name="SUBWAY BAKIRKOY",
                district="Bakırköy",
                address="Capacity AVM",
                platform_origin="Getir",
                current_risk_status=RiskStatus.SAFE,
                total_complaints=1,
                total_orders=165,
                avg_rating=4.2,
                latitude=40.9807,
                longitude=28.8738,
                is_active=True
            ),
        ]
        
        db.add_all(restaurants)
        await db.commit()
        
        print(f"✅ Seeded {len(restaurants)} test restaurants")


async def seed_all():
    """Seed all test data"""
    print("🌱 Starting seed process...")
    
    dorm_id = await seed_dormitories()
    await seed_restaurants()
    if dorm_id:
        await seed_users(dorm_id)
    
    print("✅ Seed process completed!")


if __name__ == "__main__":
    asyncio.run(seed_all())
