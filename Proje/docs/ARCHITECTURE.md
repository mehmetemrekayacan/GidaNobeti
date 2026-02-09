# 🏗️ GIDA NÖBETİ - MİMARİ DÖKÜMANI

**Hedef:** Yeni geliştiricilerin projeyi hızla anlaması için teknik mimari özeti.  
**Son Güncelleme:** 9 Şubat 2026

---

## 1. GENEL MİMARİ

```
┌─────────────────────────────────────────────────────────────┐
│  CLIENT LAYER                                                │
│  Mobile (Flutter) + Admin Panel (Next.js)                    │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTPS
┌─────────────────────────▼───────────────────────────────────┐
│  APPLICATION LAYER (FastAPI)                                 │
│  API (v1) → Services → Models                               │
│  Schemas (Pydantic) | Auth (JWT) | Rate Limit (Redis)       │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│  DATA LAYER                                                 │
│  PostgreSQL 16 (Async) | Redis (Cache/Session)             │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. KLASÖR YAPISI

```
Proje/
├── backend/                    # FastAPI API
│   ├── app/
│   │   ├── api/v1/             # Endpoint'ler (auth, orders, restaurants, admin, incidents)
│   │   ├── core/               # config, security, deps, limiter, middleware
│   │   ├── db/
│   │   │   ├── models/         # SQLAlchemy modelleri
│   │   │   └── session.py     # Async DB session
│   │   ├── schemas/            # Pydantic request/response
│   │   ├── services/           # İş mantığı (OCR, parser, restaurant, risk)
│   │   └── main.py
│   ├── alembic/                # DB migrations
│   └── requirements.txt
├── admin-panel/                # Next.js (React/TypeScript)
├── mobile/                     # Flutter (Dart)
└── docs/                       # Dokümantasyon
```

---

## 3. VERİTABANI ŞEMASI

### 3.1 ER İlişkileri

```
dormitories (1) ────< (N) users
users (1) ────< (N) orders
users (1) ────< (N) health_incidents
restaurants (1) ────< (N) orders
orders (1) ────< (N) order_items
orders (1) ────< (N) health_incidents (suspected_order_id)
```

### 3.2 Tablolar

| Tablo | Açıklama | Anahtar |
|-------|----------|---------|
| `dormitories` | Yurtlar | id (SERIAL) |
| `users` | Kullanıcılar | id (UUID) |
| `restaurants` | Restoranlar | id (SERIAL) |
| `orders` | Siparişler | id (UUID) |
| `order_items` | Sipariş detayları | id (SERIAL) |
| `health_incidents` | Sağlık vakaları | id (UUID) |

### 3.3 Raporlama VIEW'ları

| VIEW | Açıklama |
|------|----------|
| `view_daily_statistics` | Yurt bazlı günlük sipariş/incident özeti (son 30 gün) |
| `view_risky_restaurants` | RED_FLAG/BLACKLISTED restoranlar + şikayet oranı |

---

## 4. KATMAN AKIŞI

### API → Service → Model

```
Endpoint (orders.py)
    │
    ├── Depends(get_db)           → AsyncSession
    ├── Depends(get_current_user) → User
    │
    ├── Service çağrısı (ocr_service, restaurant_service)
    │
    ├── Model işlemleri (Order, OrderItem)
    │
    └── Schema ile response (OrderUploadResponse)
```

### Örnek: Sipariş Yükleme

1. `POST /v1/orders/upload` → `upload_receipt()`
2. `ocr_service.extract()` → RAM'de OCR (görsel saklanmaz)
3. `parser_service.parse()` → restoran, tutar, ürünler
4. `find_or_create_restaurant()` → restoran bul/oluştur
5. `Order` + `OrderItem` kaydet
6. `OrderUploadResponse` döndür

---

## 5. GÜVENLİK (KVKK)

- **Görsel saklama:** Yok. OCR RAM'de işlenir, hemen silinir.
- **TCKN:** Hash'lenerek saklanır (`tckn_hash`).
- **JWT:** `python-jose` ile access token.
- **Rate Limit:** `slowapi` + Redis.

---

## 6. KONFIGÜRASYON

| Ortam Değişkeni | Açıklama |
|-----------------|----------|
| `DATABASE_URL` | PostgreSQL async URL (`postgresql+asyncpg://`) |
| `REDIS_URL` | Redis bağlantı URL'i |
| `SECRET_KEY` | JWT imzalama anahtarı |
| `DEBUG` | Swagger/docs açık mı |

---

## 7. MİGRASYON ve BAŞLATMA

```bash
# Migration çalıştır
docker exec -it gidanobeti_api alembic upgrade head

# Yeni migration oluştur
alembic revision --autogenerate -m "açıklama"
```

---

## 8. İLGİLİ DÖKÜMANLAR

| Dosya | İçerik |
|-------|--------|
| [SPEC.md](SPEC.md) | Tam API ve veritabanı spesifikasyonu |
| [TASKS.md](TASKS.md) | Görev listesi |
| [GELISTIRME_ORTAMI.md](GELISTIRME_ORTAMI.md) | Kurulum ve günlük başlatma |
