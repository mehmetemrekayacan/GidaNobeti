"""
Seed test restaurant data
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.db.models.restaurant import Restaurant, RiskStatus


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


if __name__ == "__main__":
    asyncio.run(seed_restaurants())
