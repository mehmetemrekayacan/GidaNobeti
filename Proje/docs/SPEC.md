# 📘 GIDA NÖBETİ - TEKNİK SPESİFİKASYON DOKÜMANI

**Proje:** Gıda Nöbeti | Yurt Gıda Güvenliği Platformu  
**Versiyon:** 1.0.0 (MVP)  
**Tarih:** 21 Ocak 2026  
**Hazırlayanlar:** Mehmet Emre Kayacan & Mehmet Kurt

---

## 📋 İÇİNDEKİLER

1. [Sistem Mimarisi](#1-sistem-mimarisi)
2. [Teknoloji Stack](#2-teknoloji-stack)
3. [Veritabanı Şeması](#3-veritabanı-şeması)
4. [API Spesifikasyonu](#4-api-spesifikasyonu)
5. [Güvenlik Protokolleri](#5-güvenlik-protokolleri)
6. [Modül Detayları](#6-modül-detayları)
7. [Deployment](#7-deployment)
8. [Performans Gereksinimleri](#8-performans-gereksinimleri)

---

## 1. SISTEM MIMARISI

### 1.1 Genel Mimari (High-Level Architecture)

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT LAYER                              │
├──────────────────────┬──────────────────────────────────────┤
│  Mobile App          │  Web Dashboard                        │
│  (Flutter/Dart)      │  (React/Next.js - Future)            │
│  - Öğrenci Arayüzü   │  - Yurt Müdürü Paneli                │
│  - Tablet (Güvenlik) │  - Admin Paneli                       │
└──────────────────────┴──────────────────────────────────────┘
                           ↓ HTTPS (TLS 1.3)
┌─────────────────────────────────────────────────────────────┐
│               APPLICATION LAYER (Backend)                    │
├─────────────────────────────────────────────────────────────┤
│  API Gateway (Nginx)                                         │
│  ├── Rate Limiting & DDoS Protection                         │
│  └── Load Balancing                                          │
│                                                              │
│  FastAPI Server (Python 3.11+)                              │
│  ├── Authentication Service (JWT)                           │
│  ├── Order Management Service                               │
│  ├── OCR Processing Service (EasyOCR/PaddleOCR)            │
│  ├── Risk Analysis Engine                                   │
│  └── Notification Service                                   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    DATA LAYER                                │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL 16 (Primary Database)                           │
│  ├── User Data (Encrypted)                                  │
│  ├── Orders (Text-only, NO images)                          │
│  ├── Restaurants & Risk Status                              │
│  └── Health Incidents                                        │
│                                                              │
│  Redis (Cache & Session Store)                              │
│  └── Rate Limiting & Active Sessions                        │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Mimari Prensipler

- **Privacy by Design**: Görüntüler sunucuda saklanmaz
- **Data Minimization**: Sadece gerekli veriler tutulur
- **Separation of Concerns**: Her servis tek sorumlulukla çalışır
- **Horizontal Scalability**: Docker Swarm/Kubernetes ile ölçeklenebilir
- **Fail-Safe Design**: OCR hatalarında manuel kayıt seçeneği

---

## 2. TEKNOLOJI STACK

### 2.1 Mobile (Flutter)

```yaml
# pubspec.yaml dependencies
dependencies:
  flutter: sdk
  
  # State Management
  flutter_bloc: ^8.1.3         # Business Logic Component
  equatable: ^2.0.5            # Value equality için
  
  # Network & API
  dio: ^5.4.0                  # HTTP Client
  retrofit: ^4.0.0             # Type-safe API client
  json_annotation: ^4.8.1      # JSON serialization
  
  # Local Storage
  flutter_secure_storage: ^9.0.0  # JWT token storage
  shared_preferences: ^2.2.2      # Basit key-value storage
  
  # Camera & Image
  image_picker: ^1.0.7         # Galeri/Kamera erişimi
  camera: ^0.10.5+9            # Custom kamera UI için
  image_cropper: ^5.0.1        # Görüntü kırpma
  
  # UI Components
  google_fonts: ^6.1.0         # Custom fontlar
  flutter_svg: ^2.0.9          # SVG icon support
  cached_network_image: ^3.3.1 # Image caching
  shimmer: ^3.0.0              # Loading skeleton
  
  # Navigation
  go_router: ^13.0.0           # Declarative routing
  
  # Utils
  intl: ^0.19.0                # Tarih formatları
  uuid: ^4.3.3                 # UUID generation
  logger: ^2.0.2+1             # Debug logging

dev_dependencies:
  build_runner: ^2.4.8         # Code generation
  json_serializable: ^6.7.1    # JSON code gen
  flutter_launcher_icons: ^0.13.1  # App icon
```

**Neden Flutter?**
- Single codebase (iOS + Android)
- Native performans
- Hızlı geliştirme (Hot Reload)
- Kamera ve OCR entegrasyonu kolay
- Offline çalışma desteği

### 2.2 Backend (Python)

```txt
# requirements.txt
# Core Framework
fastapi==0.109.0             # Modern async API framework
uvicorn[standard]==0.27.0    # ASGI server
pydantic==2.6.0              # Data validation
pydantic-settings==2.1.0     # Environment config

# Database
sqlalchemy==2.0.25           # ORM
asyncpg==0.29.0              # PostgreSQL async driver
alembic==1.13.1              # Database migrations
psycopg2-binary==2.9.9       # PostgreSQL adapter

# Authentication & Security
python-jose[cryptography]==3.3.0  # JWT tokens
passlib[bcrypt]==1.7.4            # Password hashing
python-multipart==0.0.6           # File upload support

# OCR & Image Processing
easyocr==1.7.1               # OCR engine (CRITICAL)
paddleocr==2.7.0.3           # Alternative OCR
pillow==10.2.0               # Image manipulation
opencv-python-headless==4.9.0.80  # Image preprocessing

# Caching & Queue
redis==5.0.1                 # Redis client
celery==5.3.6                # Task queue (future)

# Monitoring & Logging
python-dotenv==1.0.0         # .env file support
loguru==0.7.2                # Better logging

# Testing
pytest==7.4.4                # Test framework
pytest-asyncio==0.23.3       # Async test support
httpx==0.26.0                # Async HTTP client for tests
```

**Neden Python + FastAPI?**
- Async/await desteği (yüksek concurrency)
- OCR kütüphaneleriyle kolay entegrasyon
- Type hints ile güvenli kod
- Otomatik API dokümantasyonu (Swagger)
- Hızlı geliştirme

### 2.3 Database & Infrastructure

| Teknoloji | Versiyon | Kullanım |
|-----------|----------|----------|
| **PostgreSQL** | 16.x | Ana veritabanı, JSONB support |
| **Redis** | 7.x | Session store, rate limiting |
| **Nginx** | 1.25.x | Reverse proxy, load balancer |
| **Docker** | 24.x | Containerization |
| **Docker Compose** | 2.x | Multi-container orchestration |

---

## 3. VERİTABANI ŞEMASI

### 3.1 ER Diagram

```
┌─────────────────┐         ┌──────────────────┐
│  dormitories    │         │   restaurants    │
├─────────────────┤         ├──────────────────┤
│ id (PK)         │         │ id (PK)          │
│ name            │         │ name             │
│ city            │         │ district         │
│ capacity        │         │ platform_origin  │
│ is_active       │         │ risk_status      │
└────────┬────────┘         │ total_complaints │
         │                  └────────┬─────────┘
         │ 1:N                       │
         │                           │ N:1
┌────────▼────────┐         ┌────────▼─────────┐
│     users       │         │     orders       │
├─────────────────┤         ├──────────────────┤
│ id (UUID, PK)   │◄───────┤│ id (UUID, PK)    │
│ dorm_id (FK)    │   N:1  ││ user_id (FK)     │
│ tckn_hash       │        ││ restaurant_id(FK)│
│ full_name       │        ││ declared_at      │
│ room_number     │        ││ receipt_date     │
│ phone_number    │        ││ method           │
│ role            │        ││ total_amount     │
│ is_active       │        ││ raw_ocr_text     │
└────────┬────────┘        │└──────────────────┘
         │                 │         │ 1:N
         │ 1:N             │         │
         │                 │ ┌───────▼──────────┐
         │                 │ │   order_items    │
         │                 │ ├──────────────────┤
         │                 │ │ id (PK)          │
         │                 │ │ order_id (FK)    │
         │                 │ │ item_name        │
         │                 │ │ quantity         │
         │                 │ └──────────────────┘
         │                 │
         │ 1:N             │ N:1
┌────────▼────────┐       │
│health_incidents │       │
├─────────────────┤       │
│ id (UUID, PK)   │       │
│ user_id (FK)    ├───────┘
│ suspected_order │
│ symptoms        │
│ report_date     │
│ status          │
│ admin_notes     │
└─────────────────┘
```

### 3.2 Tablo Detayları

#### **dormitories** (Yurtlar)
```sql
CREATE TABLE dormitories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL DEFAULT 'Isparta',
    district VARCHAR(100),
    address TEXT,
    capacity INT,
    phone VARCHAR(20),
    latitude DECIMAL(10, 8),  -- Harita için
    longitude DECIMAL(11, 8),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dormitories_city ON dormitories(city);
CREATE INDEX idx_dormitories_active ON dormitories(is_active);
```

#### **users** (Kullanıcılar)
```sql
-- UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enum types
CREATE TYPE user_role AS ENUM ('STUDENT', 'DORM_MANAGER', 'SECURITY', 'SYS_ADMIN');

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dorm_id INT REFERENCES dormitories(id),
    
    -- Kimlik Bilgileri (Şifrelenmiş)
    tckn_hash VARCHAR(255) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone_number VARCHAR(20),
    
    -- Yurt Bilgisi
    room_number VARCHAR(20),
    
    -- Authentication
    password_hash VARCHAR(255) NOT NULL,
    role user_role DEFAULT 'STUDENT',
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    
    -- Activity Tracking
    last_login_at TIMESTAMPTZ,
    login_attempts INT DEFAULT 0,
    lockout_until TIMESTAMPTZ,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

CREATE INDEX idx_users_tckn_hash ON users(tckn_hash);
CREATE INDEX idx_users_dorm ON users(dorm_id);
CREATE INDEX idx_users_role ON users(role);
```

#### **restaurants** (Restoranlar)
```sql
CREATE TYPE risk_status AS ENUM ('SAFE', 'WATCHLIST', 'RED_FLAG', 'BLACKLISTED');

CREATE TABLE restaurants (
    id SERIAL PRIMARY KEY,
    
    -- Temel Bilgiler
    name VARCHAR(255) NOT NULL,
    normalized_name VARCHAR(255),  -- OCR için normalize edilmiş (UPPERCASE, trim)
    district VARCHAR(100),
    address TEXT,
    
    -- Kaynak Platform
    platform_origin VARCHAR(50),  -- 'Trendyol', 'Getir', 'Yerel', vb.
    
    -- Risk Yönetimi
    current_risk_status risk_status DEFAULT 'SAFE',
    risk_updated_at TIMESTAMPTZ,
    risk_reason TEXT,
    total_complaints INT DEFAULT 0,
    total_orders INT DEFAULT 0,
    
    -- Coğrafi Bilgiler
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    
    -- İstatistikler
    avg_rating DECIMAL(3, 2),
    
    -- Metadata
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_restaurants_name ON restaurants(normalized_name);
CREATE INDEX idx_restaurants_risk ON restaurants(current_risk_status);
CREATE INDEX idx_restaurants_platform ON restaurants(platform_origin);
CREATE INDEX idx_restaurants_location ON restaurants USING GIST (
    point(longitude, latitude)
);
```

#### **orders** (Siparişler - CORE TABLE)
```sql
CREATE TYPE entry_method AS ENUM ('SCREENSHOT', 'PHYSICAL_RECEIPT', 'MANUAL_ENTRY');

CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    restaurant_id INT REFERENCES restaurants(id),
    
    -- Zaman Bilgileri
    declared_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,  -- Sisteme yükleme zamanı
    receipt_date TIMESTAMPTZ,                           -- Fişteki gerçek tarih
    
    -- Kanıt ve İçerik
    method entry_method NOT NULL,
    raw_ocr_text TEXT,                    -- OCR çıktısı (görsel DEĞİL!)
    ocr_confidence DECIMAL(5, 2),         -- OCR güven skoru (0-100)
    manual_note TEXT,                     -- Kullanıcının eklediği not
    
    -- Mali Bilgi
    total_amount DECIMAL(10, 2),
    
    -- Güvenlik & Tracking
    client_ip INET,
    user_agent VARCHAR(255),
    device_id VARCHAR(255),
    gps_latitude DECIMAL(10, 8),
    gps_longitude DECIMAL(11, 8),
    
    -- Durum
    is_verified BOOLEAN DEFAULT FALSE,     -- Admin onayı
    verification_notes TEXT,
    
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_restaurant ON orders(restaurant_id);
CREATE INDEX idx_orders_date ON orders(declared_at);
CREATE INDEX idx_orders_receipt_date ON orders(receipt_date);
CREATE INDEX idx_orders_method ON orders(method);
```

#### **order_items** (Sipariş Detayları)
```sql
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    
    item_name VARCHAR(255) NOT NULL,
    quantity INT DEFAULT 1,
    unit_price DECIMAL(10, 2),
    
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_order_items_order ON order_items(order_id);
```

#### **health_incidents** (Sağlık Vakaları)
```sql
CREATE TYPE report_status AS ENUM ('PENDING', 'INVESTIGATING', 'CONFIRMED', 'DISMISSED');

CREATE TABLE health_incidents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    suspected_order_id UUID REFERENCES orders(id),
    
    -- Vaka Bilgileri
    symptoms TEXT NOT NULL,
    symptom_start_time TIMESTAMPTZ,
    severity_level INT CHECK (severity_level BETWEEN 1 AND 5),
    
    -- Doktor Bilgisi
    is_verified_by_doctor BOOLEAN DEFAULT FALSE,
    doctor_name VARCHAR(100),
    doctor_notes TEXT,
    hospital_name VARCHAR(255),
    
    -- İş Akışı
    report_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    status report_status DEFAULT 'PENDING',
    admin_notes TEXT,
    resolution_date TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_incidents_user ON health_incidents(user_id);
CREATE INDEX idx_incidents_order ON health_incidents(suspected_order_id);
CREATE INDEX idx_incidents_status ON health_incidents(status);
CREATE INDEX idx_incidents_date ON health_incidents(report_date);
```

### 3.3 Views (Raporlama)

```sql
-- Dashboard için günlük özet
CREATE VIEW view_daily_statistics AS
SELECT 
    d.id as dorm_id,
    d.name as dorm_name,
    DATE(o.declared_at) as date,
    COUNT(DISTINCT o.id) as total_orders,
    COUNT(DISTINCT o.user_id) as active_students,
    COUNT(DISTINCT o.restaurant_id) as unique_restaurants,
    COUNT(DISTINCT hi.id) as total_incidents,
    SUM(o.total_amount) as total_spent
FROM dormitories d
LEFT JOIN users u ON u.dorm_id = d.id
LEFT JOIN orders o ON o.user_id = u.id
LEFT JOIN health_incidents hi ON hi.user_id = u.id 
    AND DATE(hi.report_date) = DATE(o.declared_at)
WHERE o.declared_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY d.id, d.name, DATE(o.declared_at);

-- Riskli restoranlar raporu
CREATE VIEW view_risky_restaurants AS
SELECT 
    r.id,
    r.name,
    r.current_risk_status,
    r.total_complaints,
    r.total_orders,
    ROUND((r.total_complaints::DECIMAL / NULLIF(r.total_orders, 0)) * 100, 2) as complaint_rate,
    COUNT(DISTINCT hi.id) as confirmed_incidents,
    MAX(hi.report_date) as last_incident_date
FROM restaurants r
LEFT JOIN orders o ON o.restaurant_id = r.id
LEFT JOIN health_incidents hi ON hi.suspected_order_id = o.id 
    AND hi.status = 'CONFIRMED'
WHERE r.current_risk_status IN ('RED_FLAG', 'BLACKLISTED')
GROUP BY r.id, r.name, r.current_risk_status, r.total_complaints, r.total_orders
ORDER BY r.total_complaints DESC;
```

---

## 4. API SPESİFİKASYONU

### 4.1 Base URL & Versioning

```
Production:  https://api.gidanobeti.gov.tr/v1
Development: http://localhost:8000/v1
```

### 4.2 Authentication

#### **POST /auth/register**
Yeni öğrenci kaydı.

**Request:**
```json
{
  "tckn": "12345678901",
  "password": "SecurePass123!",
  "full_name": "Ahmet Yılmaz",
  "email": "ahmet.yilmaz@example.com",
  "phone_number": "+905551234567",
  "dorm_id": 1,
  "room_number": "A-205"
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Kayıt başarılı. Email adresinizi doğrulayın.",
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### **POST /auth/login**
Giriş yapma.

**Request:**
```json
{
  "tckn": "12345678901",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "full_name": "Ahmet Yılmaz",
    "role": "STUDENT",
    "dorm_name": "Isparta Erkek KYK Yurdu"
  }
}
```

### 4.3 Orders (Siparişler)

#### **POST /orders/upload** ⭐ CRITICAL ENDPOINT

Fiş/ekran görüntüsü yükleme ve OCR işleme.

**Request (multipart/form-data):**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data

Fields:
- image: [binary file] (max 5MB)
- manual_note: "Akşam yemeği" (optional)
- gps_latitude: 37.7749 (optional)
- gps_longitude: -122.4194 (optional)
```

**Processing Flow:**
1. Görsel sunucuya yüklenir (RAM'e)
2. OCR motoru çalışır (2-5 saniye)
3. Restoran ismi normalize edilir ve veritabanında aranır
4. Bulunamazsa yeni restoran kaydı oluşturulur
5. Order kaydı oluşturulur
6. Görsel RAM'den silinir
7. Yanıt döner

**Response (201):**
```json
{
  "success": true,
  "order_id": "660e8400-e29b-41d4-a716-446655440001",
  "ocr_result": {
    "restaurant_name": "PASAPORT PIZZA",
    "total_amount": 85.50,
    "date": "2026-01-21T19:30:00Z",
    "items": [
      {"name": "Karışık Pizza", "quantity": 1},
      {"name": "Kola 330ml", "quantity": 2}
    ],
    "confidence_score": 92.5
  },
  "restaurant": {
    "id": 42,
    "name": "Pasaport Pizza",
    "risk_status": "SAFE"
  },
  "warnings": []
}
```

**Response (201 - Risk Detected):**
```json
{
  "success": true,
  "order_id": "660e8400-e29b-41d4-a716-446655440001",
  "ocr_result": { /* ... */ },
  "restaurant": {
    "id": 15,
    "name": "X Dönerci",
    "risk_status": "RED_FLAG"
  },
  "warnings": [
    {
      "type": "RED_FLAG",
      "message": "⚠️ DİKKAT: Bu restoran Bakanlık tarafından denetim altına alınmıştır.",
      "reason": "3 gıda zehirlenmesi vakası tespit edildi (Son 24 saat)",
      "action_required": true
    }
  ]
}
```

#### **GET /orders/my-history**
Kullanıcının sipariş geçmişi.

**Query Params:**
- `page`: int (default: 1)
- `limit`: int (default: 20, max: 100)
- `start_date`: ISO8601 timestamp (optional)
- `end_date`: ISO8601 timestamp (optional)
- `restaurant_id`: int (optional)

**Response (200):**
```json
{
  "total": 156,
  "page": 1,
  "limit": 20,
  "data": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "restaurant": {
        "id": 42,
        "name": "Pasaport Pizza",
        "risk_status": "SAFE"
      },
      "total_amount": 85.50,
      "declared_at": "2026-01-21T19:45:00Z",
      "receipt_date": "2026-01-21T19:30:00Z",
      "method": "SCREENSHOT",
      "items": [
        {"name": "Karışık Pizza", "quantity": 1}
      ]
    }
  ]
}
```

### 4.4 Restaurants (Restoranlar)

#### **GET /restaurants/risky**
Riskli restoranlar listesi (Ana sayfa için).

**Response (200):**
```json
{
  "updated_at": "2026-01-21T20:00:00Z",
  "risky_restaurants": [
    {
      "id": 15,
      "name": "X Dönerci",
      "risk_status": "RED_FLAG",
      "total_complaints": 5,
      "last_incident": "2026-01-21T14:30:00Z",
      "reason": "Gıda zehirlenmesi vakaları",
      "alert_message": "⚠️ Bu restorandan sipariş VERMEYİN!"
    },
    {
      "id": 23,
      "name": "Y Burger",
      "risk_status": "WATCHLIST",
      "total_complaints": 2,
      "alert_message": "🔍 Denetim altında"
    }
  ]
}
```

#### **GET /restaurants/search**
Restoran arama.

**Query Params:**
- `q`: string (restoran adı)
- `limit`: int (default: 10)

**Response (200):**
```json
{
  "results": [
    {
      "id": 42,
      "name": "Pasaport Pizza",
      "district": "Merkez",
      "risk_status": "SAFE",
      "total_orders": 1523,
      "avg_rating": 4.5
    }
  ]
}
```

### 4.5 Health Incidents (Sağlık Vakaları)

#### **POST /incidents/report**
Sağlık sorunu bildirimi.

**Request:**
```json
{
  "suspected_order_id": "660e8400-e29b-41d4-a716-446655440001",
  "symptoms": "Mide bulantısı, karın ağrısı, ishal",
  "symptom_start_time": "2026-01-21T22:00:00Z",
  "severity_level": 3
}
```

**Response (201):**
```json
{
  "incident_id": "770e8400-e29b-41d4-a716-446655440002",
  "message": "Şikayetiniz kaydedildi. Yurt yönetimi bilgilendirildi.",
  "next_steps": [
    "Bol su için",
    "Yurt sağlık görevlisine başvurun",
    "Şikayetler artarsa restoran otomatik olarak 'Riskli' ilan edilecek"
  ]
}
```

### 4.6 Admin Endpoints (Yurt Müdürü)

#### **GET /admin/dashboard/statistics**
Dashboard istatistikleri.

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response (200):**
```json
{
  "period": "last_7_days",
  "total_orders": 1243,
  "total_students": 458,
  "total_incidents": 3,
  "top_restaurants": [
    {"name": "Pasaport Pizza", "order_count": 287},
    {"name": "Burger King", "order_count": 156}
  ],
  "incidents_by_restaurant": [
    {"restaurant": "X Dönerci", "incident_count": 2}
  ],
  "daily_breakdown": [
    {"date": "2026-01-21", "orders": 198, "incidents": 0},
    {"date": "2026-01-20", "orders": 185, "incidents": 1}
  ]
}
```

---

## 5. GÜVENLİK PROTOKOLLERİ

### 5.1 Data Privacy (KVKK Uyumu)

#### **No-Image-Storage Policy** ⭐ EN ÖNEMLİ
```python
# YANLIŞ ❌ (Görsel diske yazılıyor)
image_path = f"uploads/{user_id}_{timestamp}.jpg"
image_file.save(image_path)
ocr_result = process_ocr(image_path)

# DOĞRU ✅ (Görsel sadece RAM'de)
image_bytes = await image_file.read()  # RAM'e yükle
ocr_result = process_ocr_from_bytes(image_bytes)  # İşle
del image_bytes  # Hemen sil
```

#### Hassas Veri Şifreleme
```python
# TCKN Hash (SHA-256 + Salt)
from passlib.hash import argon2

tckn_hash = argon2.hash(tckn + SECRET_SALT)

# Şifre Hashing
password_hash = argon2.hash(plain_password)
```

### 5.2 Authentication & Authorization

#### JWT Token Structure
```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",  // User ID
  "role": "STUDENT",
  "dorm_id": 1,
  "iat": 1705862400,  // Issued At
  "exp": 1705866000,  // Expires (1 hour)
  "jti": "unique-token-id"  // Token ID (revocation için)
}
```

#### Permission Matrix

| Endpoint | STUDENT | SECURITY | DORM_MANAGER | SYS_ADMIN |
|----------|---------|----------|--------------|-----------|
| POST /orders/upload | ✅ | ❌ | ❌ | ✅ |
| GET /orders/my-history | ✅ (own) | ❌ | ✅ (all) | ✅ |
| POST /incidents/report | ✅ | ❌ | ❌ | ✅ |
| GET /admin/dashboard | ❌ | ❌ | ✅ | ✅ |
| PUT /restaurants/risk-status | ❌ | ❌ | ✅ | ✅ |

### 5.3 Rate Limiting

```python
# Redis-based rate limiting
limits = {
    "/auth/login": "5 per minute",          # Brute-force koruması
    "/orders/upload": "10 per hour",        # Spam koruması
    "/incidents/report": "3 per hour",      # Abuse koruması
    "global": "100 per minute per IP"       # DDoS koruması
}
```

### 5.4 Network Security

#### HTTPS Enforcement
```nginx
# nginx.conf
server {
    listen 80;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    ssl_certificate /etc/ssl/cert.pem;
    ssl_certificate_key /etc/ssl/key.pem;
    ssl_protocols TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
}
```

#### CORS Policy
```python
allowed_origins = [
    "https://app.gidanobeti.gov.tr",  # Production mobile
    "http://localhost:*",              # Development
]
```

---

## 6. MODÜL DETAYLARI

### 6.1 OCR Processing Service

#### Desteklenen Formatlar
- JPEG/JPG (max 5MB)
- PNG (max 5MB)
- HEIC/HEIF (iOS - otomatik dönüşüm)

#### Image Preprocessing Pipeline
```python
def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """
    Görüntüyü OCR için optimize et
    """
    # 1. Load image
    image = Image.open(io.BytesIO(image_bytes))
    
    # 2. Convert to grayscale
    image = image.convert('L')
    
    # 3. Resize (max 1920x1080)
    if image.width > 1920:
        ratio = 1920 / image.width
        new_height = int(image.height * ratio)
        image = image.resize((1920, new_height), Image.LANCZOS)
    
    # 4. Enhance contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.5)
    
    # 5. Denoise
    image_array = np.array(image)
    image_array = cv2.fastNlMeansDenoising(image_array, None, 10, 7, 21)
    
    return image_array
```

#### OCR Engine Selection
```python
# EasyOCR (Primary - Türkçe desteği iyi)
reader = easyocr.Reader(['tr', 'en'], gpu=True)

# PaddleOCR (Fallback - Hızlı ama Türkçe zayıf)
paddle_reader = PaddleOCR(lang='tr', use_gpu=True)

# Hybrid Approach
def perform_ocr(image: np.ndarray) -> dict:
    # Try EasyOCR first
    result = reader.readtext(image)
    confidence = calculate_avg_confidence(result)
    
    # If low confidence, try PaddleOCR
    if confidence < 0.7:
        result = paddle_reader.ocr(image)
    
    return parse_ocr_result(result)
```

#### Text Parsing Logic
```python
def extract_restaurant_name(ocr_text: str) -> str:
    """
    OCR metninden restoran ismini çıkar
    """
    # Pattern 1: Büyük harflerle yazılmış başlık
    match = re.search(r'\b[A-ZĞÜŞÖÇI]{2,}(?:\s+[A-ZĞÜŞÖÇI]{2,})*\b', ocr_text)
    if match:
        return match.group()
    
    # Pattern 2: "Restaurant:" keyword
    match = re.search(r'(?:Restaurant|Restoran|İşletme):\s*(.+)', ocr_text, re.I)
    if match:
        return match.group(1).strip()
    
    # Pattern 3: İlk satır (genellikle restoran ismi)
    lines = ocr_text.strip().split('\n')
    return lines[0] if lines else "Bilinmeyen Restoran"

def extract_total_amount(ocr_text: str) -> Optional[float]:
    """
    Toplam tutarı bul
    """
    patterns = [
        r'Toplam[:\s]+(\d+[.,]\d{2})',
        r'TOTAL[:\s]+(\d+[.,]\d{2})',
        r'(\d+[.,]\d{2})\s*TL',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, ocr_text, re.I)
        if match:
            amount_str = match.group(1).replace(',', '.')
            return float(amount_str)
    
    return None
```

### 6.2 Risk Analysis Engine

#### Algoritma: Otomatik Risk Statüsü Güncelleme

```python
async def update_restaurant_risk_status(restaurant_id: int):
    """
    Restoran risk seviyesini otomatik güncelle
    """
    # 1. Son 24 saatteki şikayetleri say
    recent_incidents = await db.count_incidents(
        restaurant_id=restaurant_id,
        since=datetime.now() - timedelta(hours=24)
    )
    
    # 2. Toplam sipariş sayısına göre oran hesapla
    total_orders = await db.count_orders(restaurant_id=restaurant_id)
    complaint_rate = recent_incidents / max(total_orders, 1)
    
    # 3. Risk seviyesi belirle
    if recent_incidents >= 3:
        new_status = RiskStatus.RED_FLAG
        reason = f"{recent_incidents} vaka tespit edildi (Son 24 saat)"
        
    elif recent_incidents >= 2:
        new_status = RiskStatus.WATCHLIST
        reason = f"{recent_incidents} şikayet alındı. İzleme altında."
        
    elif complaint_rate > 0.05:  # %5'ten fazla
        new_status = RiskStatus.WATCHLIST
        reason = f"Şikayet oranı yüksek (%{complaint_rate*100:.1f})"
        
    else:
        new_status = RiskStatus.SAFE
        reason = None
    
    # 4. Veritabanını güncelle
    await db.update_restaurant_status(
        restaurant_id=restaurant_id,
        status=new_status,
        reason=reason
    )
    
    # 5. Eğer RED_FLAG ise, bildirim gönder
    if new_status == RiskStatus.RED_FLAG:
        await notification_service.send_alert(
            type="RED_FLAG_RESTAURANT",
            restaurant_id=restaurant_id,
            target="ALL_STUDENTS"
        )
```

#### Trigger: Şikayet Sonrası Otomatik Çalışma

```sql
-- PostgreSQL Trigger
CREATE OR REPLACE FUNCTION check_restaurant_risk()
RETURNS TRIGGER AS $$
BEGIN
    -- Yeni incident eklendiğinde, restoranın risk statüsünü güncelle
    PERFORM pg_notify(
        'risk_check_queue',
        json_build_object(
            'restaurant_id', NEW.suspected_order_id
        )::text
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_incident_insert
AFTER INSERT ON health_incidents
FOR EACH ROW
EXECUTE FUNCTION check_restaurant_risk();
```

---

## 7. DEPLOYMENT

### 7.1 Docker Compose (Development)

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Backend API
  api:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://gidanobeti:secure_pass@db:5432/gidanobeti_db
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: ${SECRET_KEY}
      OCR_ENABLE_GPU: "false"
    volumes:
      - ./backend:/app
    depends_on:
      - db
      - redis
    command: uvicorn app.main:app --host 0.0.0.0 --reload

  # PostgreSQL Database
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: gidanobeti
      POSTGRES_PASSWORD: secure_pass
      POSTGRES_DB: gidanobeti_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/db/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"

  # Redis Cache
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # Nginx (Production için)
  nginx:
    image: nginx:1.25-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/ssl:ro
    depends_on:
      - api

volumes:
  postgres_data:
  redis_data:
```

### 7.2 Production Deployment (Docker Swarm)

```bash
# 1. Swarm initialize
docker swarm init

# 2. Secret management
echo "super_secret_jwt_key" | docker secret create jwt_secret -
echo "db_password_here" | docker secret create db_password -

# 3. Deploy stack
docker stack deploy -c docker-compose.prod.yml gidanobeti

# 4. Scale services
docker service scale gidanobeti_api=3

# 5. Monitor
docker service logs -f gidanobeti_api
```

### 7.3 Sistem Gereksinimleri

#### Pilot (2.000 Kullanıcı)
- **CPU**: 4 Core (Intel Xeon veya AMD EPYC)
- **RAM**: 8 GB
- **Storage**: 50 GB SSD
- **Network**: 100 Mbps
- **OS**: Ubuntu 22.04 LTS

#### Production (850.000 Kullanıcı)
- **Load Balancer**: Nginx (2x 2 Core, 4GB RAM)
- **API Servers**: 10x (4 Core, 8GB RAM)
- **Database**: PostgreSQL (8 Core, 32GB RAM, 500GB SSD)
- **Redis**: 2x (2 Core, 8GB RAM) - Master/Replica
- **Total**: ~100 Core, 200GB RAM

---

## 8. PERFORMANS GEREKSİNİMLERİ

### 8.1 Response Time SLA

| Endpoint | Target | Max Acceptable |
|----------|--------|----------------|
| GET /restaurants/risky | < 200ms | 500ms |
| POST /orders/upload | < 5s | 10s |
| GET /orders/my-history | < 300ms | 1s |
| POST /auth/login | < 500ms | 1s |

### 8.2 Throughput

- **Concurrent Users**: 5.000 aktif kullanıcı
- **Peak Load**: 500 req/sec (akşam yemeği saati)
- **OCR Queue**: 100 görüntü/dakika işleme kapasitesi

### 8.3 Availability

- **Uptime**: 99.5% (yıllık 43.8 saat downtime)
- **Database Backup**: Günlük tam, saatlik incremental
- **Disaster Recovery**: 4 saat RTO, 1 saat RPO

---

## 9. MONITORING & LOGGING

### 9.1 Metrics to Track

```python
# Prometheus metrics
ocr_processing_time = Histogram('ocr_processing_seconds')
order_upload_total = Counter('order_uploads_total')
risk_flag_triggers = Counter('risk_flags_total', ['restaurant_id'])
api_request_duration = Histogram('api_request_duration_seconds', ['endpoint'])
```

### 9.2 Logging Strategy

```python
# Structured logging with loguru
logger.info(
    "Order uploaded",
    extra={
        "user_id": user_id,
        "order_id": order_id,
        "restaurant_id": restaurant_id,
        "ocr_confidence": 92.5,
        "processing_time_ms": 3420
    }
)
```

---

## 10. GELECEK ÖZELLIKLER (v2.0+)

- [ ] AI-powered restoran öneri sistemi
- [ ] Blockchain tabanlı tamperproof kayıt
- [ ] QR kod ile kurye doğrulama
- [ ] Gerçek zamanlı video stream (yemek hazırlama)
- [ ] Ödeme sistemi entegrasyonu (cashback)
- [ ] Multi-language support (İngilizce, Arapça)

---

**Son Güncelleme:** 21 Ocak 2026  
**Sorumlu:** Mehmet Emre Kayacan & Mehmet Kurt  
**Durum:** ✅ Geliştirme Hazır
