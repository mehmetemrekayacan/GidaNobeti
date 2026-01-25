# 🔧 DEMO LOGIN HATASI ÇÖZÜMÜ

## Sorunlar

### Sorun 1: Login 401 Hatası
Login 401 hatası alınıyor - Kullanıcılar seed edilmemiş veya şifre hash'i yanlış olabilir.

### Sorun 2: "Bu panel sadece yöneticiler içindir" Hatası
Login başarılı ama kullanıcı `STUDENT` rolünde. Admin paneli için `DORM_MANAGER` veya `SYS_ADMIN` rolü gerekli.

## Çözüm

### Adım 1: Seed Script'i Tekrar Çalıştır
```bash
docker exec -it gidanobeti_api python seed_restaurants.py
```

**Beklenen Çıktı:**
```
🌱 Starting seed process...
✅ Seeded dormitory: Isparta Erkek KYK Yurdu
✅ 10 restaurants already exist, skipping seed
✅ Admin user already exists (TCKN: 11111111111)
   ✅ Admin password is correct
   ✅ Admin role is correct
✅ Student user already exists (TCKN: 12345678901)
   ✅ Student password is correct

📋 Test Kullanıcıları:
   Admin: TCKN=11111111111, Password=Admin123!
   Student: TCKN=12345678901, Password=Test123!
✅ Seed process completed!
```

**Eğer admin rolü yanlışsa:**
```
✅ Admin user already exists (TCKN: 11111111111)
   ⚠️ Admin role is STUDENT, updating to DORM_MANAGER...
   ✅ Admin role and status updated
```

Bu durumda seed script admin kullanıcısının rolünü otomatik olarak `DORM_MANAGER` yapacak.

### Adım 2: Login Test Et

**Swagger UI'da Test:**
1. http://localhost:8000/docs aç
2. `POST /v1/auth/login` endpoint'ini aç
3. "Try it out" tıkla
4. Request body:
```json
{
  "tckn": "11111111111",
  "password": "Admin123!"
}
```
5. Execute → Token almalı

**Admin Panel'de Test:**
1. http://localhost:3000/login aç
2. TCKN: `11111111111`
3. Şifre: `Admin123!`
4. Giriş yap → Dashboard'a yönlendirilmeli

---

## Eğer Hala 401 Hatası Alırsanız

### Kullanıcıları Manuel Oluştur

Docker container içinde Python shell aç:
```bash
docker exec -it gidanobeti_api python
```

Sonra şunu çalıştır:
```python
import asyncio
from app.db.session import AsyncSessionLocal
from app.db.models.user import User, UserRole
from app.db.models.dormitory import Dormitory
from app.core.security import hash_tckn, hash_password
from sqlalchemy import select

async def create_admin():
    async with AsyncSessionLocal() as db:
        # Get dormitory
        dorm_query = select(Dormitory).limit(1)
        dorm_result = await db.execute(dorm_query)
        dorm = dorm_result.scalar_one()
        
        # Check if admin exists
        admin_tckn = hash_tckn("11111111111")
        user_query = select(User).where(User.tckn_hash == admin_tckn)
        user_result = await db.execute(user_query)
        existing = user_result.scalar_one_or_none()
        
        if existing:
            print(f"Admin user exists, updating password...")
            existing.password_hash = hash_password("Admin123!")
            existing.role = UserRole.DORM_MANAGER
            existing.is_active = True
            existing.is_verified = True
        else:
            print("Creating admin user...")
            admin = User(
                dorm_id=dorm.id,
                tckn_hash=admin_tckn,
                password_hash=hash_password("Admin123!"),
                full_name="Yurt Müdürü",
                email="mudur@test.com",
                phone_number="05551111111",
                role=UserRole.DORM_MANAGER,
                is_active=True,
                is_verified=True
            )
            db.add(admin)
        
        await db.commit()
        print("✅ Admin user ready!")

asyncio.run(create_admin())
```

---

## Kontrol Listesi

- [ ] Seed script çalıştı mı?
- [ ] Admin kullanıcı oluşturuldu mu?
- [ ] Admin kullanıcının rolü `DORM_MANAGER` mı? (Swagger'da login yapıp response'daki `user.role` kontrol et)
- [ ] Şifre hash'i doğru mu?
- [ ] Swagger'da login çalışıyor mu?
- [ ] Admin panel'de login çalışıyor mu?

---

**Son Güncelleme:** 25 Ocak 2026
