# ✅ SİPARİŞ TAKİP UYGULAMASI - DETAYLI GÖREV LİSTESİ (TASKS)

**Proje:** Sipariş Takip Uygulaması | Yurt Gıda Güvenliği ve Kapı Düzeni Sistemi  
**Son Güncelleme:** 8 Şubat 2026  
**Durum:** 🚧 Demo Aşamasında | Order History + Health Incident ✅ Tamamlandı

---

## 🧭 Güncel Durum Özeti (Şubat 2026)

**Son tamamlanan (admin + demo UI) işleri:**
- ✅ Orders sayfası gerçek API bağlantısı (`GET /admin/orders`)
- ✅ Orders sayfasında backend destekli sayfalama + \"Daha fazla yükle\" butonu
- ✅ Orders sayfasında demo veri fallback + \"Demo veri\" etiketi
- ✅ Dashboard periyot seçimi (Son 7 gün / Son 30 gün) + gerçek API (`GET /admin/dashboard/statistics`)
- ✅ Restaurants sayfası gerçek API bağlantısı (`GET /restaurants`, `PUT /admin/restaurants/{id}/risk-status`)
- ✅ `RestaurantListItem` şemasına `risk_reason` alanı eklendi, admin panelde gösteriliyor
- ✅ Incidents yönetim sayfası (`GET/PUT /admin/incidents`) admin panel ile entegre
- ✅ Admin kullanıcı listesi: `GET /admin/users` + `/dashboard/students` sayfası (Öğrenciler)

**Öncelikli sıradaki görevler (özet):**
- ✅ Auth guard review: Tüm `/v1/admin/*` endpoint'leri `require_admin` (DORM_MANAGER veya SYS_ADMIN) ile korunuyor
- ✅ Dashboard performansı: `/admin/dashboard/statistics` için Redis cache (10 dk, `DASHBOARD_CACHE_ENABLED`)
- ✅ Öğrenci/Yönetici UX: Öğrenci listesinde İşlemler sütununda sadece Detay butonu; detay modal (ESC ile kapanır) içinde sipariş geçmişine git linki; Siparişler sayfası `?search=` ile öğrenci adına göre açılabiliyor
- 🟡 Mobile Faz 2: Login/Register, Home (Risk Panosu), Order Upload, Order History
- 🟡 DevOps: Production server, domain + SSL, CI/CD (GitHub Actions)

Detaylar aşağıdaki ilgili task başlıklarında (Backend, Admin Panel, Mobile, DevOps) işlenmiştir.

---

## 📋 İÇİNDEKİLER

1. [Task Kategorileri](#1-task-kategorileri)
2. [Backend Tasks](#2-backend-tasks)
3. [Mobile Tasks](#3-mobile-tasks)
4. [Admin Panel Tasks](#4-admin-panel-tasks)
5. [DevOps & Infrastructure](#5-devops--infrastructure)
6. [Testing & QA](#6-testing--qa)
7. [Documentation](#7-documentation)

---

## 1. TASK KATEGORİLERİ

### Öncelik Seviyeleri
- 🔴 **P0 (Critical)**: Proje çalışması için zorunlu
- 🟡 **P1 (High)**: MVP için gerekli
- 🟢 **P2 (Medium)**: Önemli ama ertelenebilir
- ⚪ **P3 (Low)**: Nice-to-have

### Durum İşaretleri
- ⏳ **Pending**: Başlanmadı
- 🚧 **In Progress**: Devam ediyor
- ✅ **Done**: Tamamlandı
- ❌ **Blocked**: Engellendi
- ⏸️ **On Hold**: Beklemede

---

## 2. BACKEND TASKS

### 2.1 Infrastructure Setup

#### TASK-BE-001: Docker Environment Setup 🔴 P0
**Süre:** 4 saat  
**Gerçek Süre:** 1.5 saat
**Sorumlu:** Emre  
**Durum:** ✅ Done

**Açıklama:**
Geliştirme ortamı için Docker Compose kurulumu.

**Checklist:**
- [x] `docker-compose.yml` dosyası oluştur
- [x] PostgreSQL service tanımla (port 5432)
- [x] Redis service tanımla (port 6379)
- [x] Backend API service tanımla (port 8000)
- [x] Volume mounting (code hot-reload için)
- [x] Environment variables (`.env.example` dosyası)
- [x] `docker-compose up` komutuyla test et
- [x] README'de setup talimatları yaz

**Acceptance Criteria:**
- ✅ `docker-compose up -d` komutu hatasız çalışmalı
- ✅ PostgreSQL'e bağlantı kurulabilmeli
- ✅ Redis çalışıyor ve healthy durumda
- ✅ Tüm servisler health check'ten geçiyor

**Tamamlanma Notları:**
- Docker Compose başarıyla kuruldu
- PostgreSQL 16, Redis 7 ve FastAPI servisleri çalışıyor
- Health check'ler başarılı (db: healthy, redis: healthy, api: up)
- Volume mount ile hot-reload aktif

**Dependencies:** Yok

---

#### TASK-BE-002: FastAPI Project Scaffold 🔴 P0
**Süre:** 3 saat  
**Gerçek Süre:** 1 saat
**Sorumlu:** Emre  
**Durum:** ✅ Done

**Açıklama:**
FastAPI projesinin temel klasör yapısını ve konfigürasyonunu oluştur.

**Checklist:**
- [x] `backend/` klasör yapısını oluştur (SPEC'e göre)
- [x] `app/main.py` - FastAPI app instance
- [x] `app/core/config.py` - Settings (pydantic-settings)
- [x] `app/core/security.py` - JWT utilities (ileride)
- [x] `app/db/base.py` - SQLAlchemy base (ileride)
- [x] `requirements.txt` - Tüm dependencies
- [x] CORS middleware ekle
- [x] Exception handler ekle (ileride)
- [x] Health check endpoint: `GET /health`
- [x] API versioning: `/v1/...` (yapı hazır)

**Acceptance Criteria:**
- ✅ FastAPI sunucusu çalışmalı
- ✅ Swagger docs otomatik oluşturulmalı (http://localhost:8000/docs)
- ✅ `/health` endpoint 200 dönmeli

**Tamamlanma Notları:**
- FastAPI scaffold başarıyla oluşturuldu
- Clean Architecture klasör yapısı (app/core, app/api, app/db, app/services, app/schemas)
- Pydantic Settings ile environment variable yönetimi
- CORS middleware ekli
- Health check endpoint çalışıyor: {"status":"healthy","service":"Gıda Nöbeti API","version":"1.0.0"}
- Dockerfile ve .dockerignore optimize edildi (Python 3.11-slim)

**Dependencies:** TASK-BE-001

---

#### TASK-BE-003: Database Models (SQLAlchemy) 🔴 P0
**Süre:** 6 saat  
**Gerçek Süre:** 2 saat
**Sorumlu:** Emre  
**Durum:** ✅ Done

**Açıklama:**
SPEC.md'deki veritabanı şemasını SQLAlchemy ORM modelleri olarak oluştur.

**Checklist:**
- [x] `app/db/models/user.py` - User model
- [x] `app/db/models/dormitory.py` - Dormitory model
- [x] `app/db/models/restaurant.py` - Restaurant model
- [x] `app/db/models/order.py` - Order & OrderItem models
- [x] `app/db/models/incident.py` - HealthIncident model
- [x] ENUM types (user_role, risk_status, entry_method, report_status)
- [x] Relationships (foreign keys) tanımla
- [x] Indexes tanımla (performance için)
- [x] `__repr__` methods (debugging için)

**Acceptance Criteria:**
- ✅ Tüm tablolar SPEC'teki şemaya uygun olmalı
- ✅ Model validation çalışmalı
- ✅ Relationships doğru tanımlanmış olmalı

**Tamamlanma Notları:**
- 5 ana model + 4 ENUM oluşturuldu
- SQLAlchemy 2.0 Mapped syntax (type-safe)
- KVKK uyumlu: Order'da image storage YOK
- UUID: User, Order, HealthIncident
- 20+ optimized index
- Cascade delete rules + CheckConstraints
- Async support ready

**Dependencies:** TASK-BE-002

---

#### TASK-BE-004: Alembic Migrations 🔴 P0
**Süre:** 3 saat  
**Gerçek Süre:** 0.5 saat
**Sorumlu:** Emre  
**Durum:** ✅ Done

**Açıklama:**
Database migration sistemi kurulumu ve ilk migration.

**Checklist:**
- [x] Alembic initialize
- [x] `alembic.ini` konfigüre et
- [x] `env.py` - SQLAlchemy metadata import (async support)
- [x] İlk migration oluştur: `alembic revision --autogenerate`
- [x] Migration'ı uygula: `alembic upgrade head`
- [ ] Seed data script (sonraki task)
- [x] Migration test edildi
- [ ] Docker entrypoint otomatik migration (ileride)

**Acceptance Criteria:**
- ✅ `alembic upgrade head` hatasız çalıştı
- ✅ 7 tablo oluşturuldu (dormitories, users, restaurants, orders, order_items, health_incidents, alembic_version)
- ✅ Indexes, constraints, foreign keys aktif

**Tamamlanma Notları:**
- Migration ID: 6cd1533566ec_initial_database_schema.py
- app/db/session.py: AsyncSession factory + get_db()
- PostgreSQL'de tablolar doğrulandı

**Dependencies:** TASK-BE-003

**Acceptance Criteria:**
- `alembic upgrade head` hatasız çalışmalı
- Veritabanında tüm tablolar oluşturulmalı
- Seed data yüklenebilmeli

**Dependencies:** TASK-BE-003

---

### 2.2 Authentication & Authorization

#### TASK-BE-005: User Registration Endpoint 🔴 P0
**Süre:** 4 saat  
**Gerçek Süre:** ~3 saat
**Sorumlu:** Emre  
**Durum:** ✅ Done

**Açıklama:**
Yeni öğrenci kaydı için API endpoint.

**Checklist:**
- [x] `POST /v1/auth/register` endpoint
- [x] Request schema (Pydantic): `RegisterRequest`
- [x] TCKN validation (11 haneli)
- [x] Email validation
- [x] Şifre strength kontrolü (Pydantic validation)
- [x] TCKN hash (SHA-256 + salt)
- [x] Şifre hash (argon2)
- [x] Duplicate user kontrolü (TCKN zaten kayıtlı mı?)
- [ ] Email verification token oluştur (future)
- [x] Response: access_token + user info

**Acceptance Criteria:**
- Postman'den test edilebilmeli
- Hatalı input'ta validation error dönmeli
- Duplicate kayıtta 409 Conflict dönmeli
- Şifre plain text olarak kaydedilmemeli

**Dependencies:** TASK-BE-004

---

#### TASK-BE-006: User Login Endpoint 🔴 P0
**Süre:** 4 saat  
**Gerçek Süre:** ~3 saat
**Sorumlu:** Emre  
**Durum:** ✅ Done

**Açıklama:**
Kullanıcı girişi ve JWT token dönme.

**Checklist:**
- [x] `POST /v1/auth/login` endpoint
- [x] Request: `{tckn, password}`
- [x] TCKN hash ile user bul
- [x] Şifre doğrulama (argon2 verify)
- [x] Login attempt sayacı (brute-force koruması)
- [x] Account lockout (5 başarısız denemeden sonra)
- [x] JWT token oluştur (user_id, role, tckn_hash payload)
- [x] Token expiry: Configurable (default 60 dakika)
- [ ] Refresh token (future - v2)
- [x] Response: `{access_token, user: {...}}`

**Acceptance Criteria:**
- ✅ Doğru credentials ile token dönmeli
- ✅ Yanlış şifre ile 401 Unauthorized
- ✅ 5 başarısız denemede account lock (30 dakika)
- ✅ JWT decode edildiğinde user bilgileri çıkmalı

**Tamamlanma Notları:**
- Auth endpoint'leri başarıyla implement edildi
- Account lockout mekanizması çalışıyor
- JWT token generation ve validation aktif
- TCKN hash ile güvenli lookup sağlandı

**Dependencies:** TASK-BE-005

---

#### TASK-BE-007: JWT Middleware & Permissions 🟡 P1
**Süre:** 3 saat  
**Gerçek Süre:** ~1 saat  
**Sorumlu:** Emre  
**Durum:** ✅ Done

**Açıklama:**
JWT token doğrulama middleware ve role-based access control.

**Checklist:**
- [x] `app/core/deps.py` - `get_current_user` dependency
- [x] JWT token parse et (header'dan)
- [x] Token expiry kontrolü
- [ ] Blacklist kontrolü (Redis - future)
- [x] User role çıkar (STUDENT, DORM_MANAGER, etc.)
- [x] Permission dependency: `require_roles()`, `require_admin`, `require_student`
- [x] Unauthorized 401 error handler
- [x] Forbidden 403 error handler

**Acceptance Criteria:**
- Protected endpoint'lere token olmadan istek 401 dönmeli
- Yanlış role ile istek 403 dönmeli
- Expired token ile 401 dönmeli

**Tamamlanma Notları:**
- Admin endpoint'leri (dashboard, risk-status) require_admin ile korundu
- require_roles(UserRole.X, UserRole.Y) ile esnek rol kontrolü
- Auth guard review: Tüm `/v1/admin/*` route'ları (6 endpoint) require_admin ile korunuyor: dashboard/statistics, restaurants/{id}/risk-status, incidents, incidents/{id}, orders, users

**Dependencies:** TASK-BE-006

---

### 2.3 OCR & Order Processing

#### TASK-BE-008: OCR Service - EasyOCR Integration 🔴 P0
**Süre:** 8 saat (KRİTİK!)  
**Gerçek Süre:** ~4 saat  
**Sorumlu:** Mehmet  
**Durum:** ✅ Done

**Açıklama:**
Fiş/ekran görüntüsünden metin çıkarma servisi.

**Checklist:**
- [x] `app/services/ocr_service.py` oluştur
- [x] EasyOCR initialize (Türkçe + İngilizce model)
- [x] GPU kullanımı (varsa, yoksa CPU fallback)
- [x] Image preprocessing pipeline:
  - [x] RGB conversion
  - [x] Resize (max 1920px)
  - [ ] Contrast enhancement (opsiyonel)
  - [ ] Noise reduction (opsiyonel)
- [x] OCR confidence score hesaplama
- [ ] Fallback: PaddleOCR (confidence < 0.7 ise) - v2
- [x] RAM-only processing (KVKK!)
- [x] Test: Trendyol fişiyle end-to-end test
- [x] Performance: Docker container'da çalışıyor

**Acceptance Criteria:**
- ✅ Türkçe karakterleri doğru okumalı (Ş, Ğ, İ, vb.)
- ✅ Görsel sunucuya kaydedilmemeli (memory-only)
- ✅ 5MB'den büyük görsel 413 error

**Tamamlanma Notları:**
- EasyOCR 1.7.1, Pillow, NumPy requirements'a eklendi
- Lazy load, Türkçe+İngilizce dil desteği
- Docker: `pip install easyocr pillow numpy` gerekli (DEMO_FIXES.md)

**Dependencies:** TASK-BE-002

**Test Data:** 10 farklı restoran fişi (JPEG/PNG)

---

#### TASK-BE-009: OCR Text Parsing 🔴 P0
**Süre:** 6 saat  
**Gerçek Süre:** ~4 saat  
**Sorumlu:** Mehmet  
**Durum:** ✅ Done

**Açıklama:**
OCR çıktısından structured data çıkarma.

**Checklist:**
- [x] `app/services/parser_service.py` oluştur
- [x] Restoran ismi extraction (regex patterns, skip fiş başlıkları)
- [x] Toplam tutar extraction (patterns: "Toplam", "TOTAL", çok satırlı format)
- [x] Tarih/saat extraction (multiple formats)
- [x] Ürün listesi extraction (line-by-line)
- [x] Miktar parsing (adet/porsiyon)
- [x] Normalize restoran ismi (uppercase, trim)
- [x] OCR hata düzeltme (O/0, l/1, €/₺)
- [x] Telefon/destek hattı satırlarını atlama (numeric overflow önleme)
- [ ] Unit tests (pytest) - v2

**Acceptance Criteria:**
- ✅ Toplam tutar float olarak dönmeli (156,OOt → 156.00)
- ✅ Parse edilemeyen alanlar `None` olmalı
- ✅ Trendyol fiş formatı destekleniyor

**Tamamlanma Notları:**
- SKIP_PATTERNS: Sipariş Kodu, Müşteri Bilgisi, tarih, telefon vb.
- MAX_UNIT_PRICE: 10000 (telefon numarası yanlış parse önleme)
- _normalize_ocr_number: O/o→0, I/l→1

**Dependencies:** TASK-BE-008

---

#### TASK-BE-010: Restaurant Auto-Create & Matching 🟡 P1
**Süre:** 4 saat  
**Gerçek Süre:** ~2 saat  
**Sorumlu:** Emre  
**Durum:** ✅ Done

**Açıklama:**
OCR'dan gelen restoran ismini veritabanında ara, yoksa oluştur.

**Checklist:**
- [x] `app/services/restaurant_service.py` oluştur
- [x] `find_or_create_restaurant()` fonksiyonu
- [x] Tam eşleşme (normalized_name)
- [ ] Fuzzy matching (Levenshtein) - v2
- [x] Normalization (uppercase, trim)
- [x] Eğer bulunamazsa yeni restaurant kaydı oluştur
- [x] Default values: risk_status='SAFE', platform_origin='Bilinmiyor'
- [ ] Admin approval (future - v2)

**Acceptance Criteria:**
- ✅ Yeni restoran otomatik oluşmalı
- ✅ normalized_name ile tam eşleşme

**Tamamlanma Notları:**
- Tam eşleşme (fuzzy v2'de eklenecek)
- orders.py'de hata durumunda restaurant=None fallback

**Dependencies:** TASK-BE-009

---

#### TASK-BE-011: Order Upload Endpoint 🔴 P0 (EN ÖNEMLİ!)
**Süre:** 6 saat  
**Gerçek Süre:** ~4 saat  
**Sorumlu:** Emre + Mehmet  
**Durum:** ✅ Done

**Açıklama:**
Fiş yükleme ve OCR processing ana endpoint.

**Checklist:**
- [x] `POST /v1/orders/upload` endpoint
- [x] Auth required (JWT)
- [x] Multipart form-data accept et
- [x] File validation (JPEG/PNG, max 5MB)
- [ ] HEIC format support (iOS - pillow-heif) - v2
- [x] Image to bytes (RAM'e yükle)
- [x] OCR service çağır
- [x] Parser service çağır
- [x] Restaurant find_or_create
- [x] Order kaydı oluştur (DB)
- [x] OrderItem kaydı oluştur
- [x] Image bytes sil (KVKK!)
- [x] Response: order_id, ocr_result, restaurant, warnings
- [x] Risk kontrolü (eğer RED_FLAG ise warning dön)
- [x] Error handling (OCR fail, DB error, global exception handler)

**Acceptance Criteria:**
- ✅ Swagger'dan görsel yüklenebilmeli
- ✅ OCR çıktısı response'ta olmalı (raw_ocr_text, ocr_confidence)
- ✅ Görsel sunucuda kalmamalı (RAM-only)
- ✅ RED_FLAG restoran için uyarı dönmeli
- ✅ Trendyol fişiyle end-to-end test başarılı

**Tamamlanma Notları:**
- DEMO_FIXES.md: Order Upload test adımları, 401/500 hata çözümleri
- Global exception handler: DEBUG modunda detaylı hata
- item_name 255 char, unit_price overflow koruması

**Dependencies:** TASK-BE-008, TASK-BE-009, TASK-BE-010

**Test:** Gerçek fiş görselleriyle end-to-end test ✅

---

#### TASK-BE-012: Order History Endpoint 🟡 P1
**Süre:** 3 saat  
**Gerçek Süre:** ~1 saat  
**Sorumlu:** Emre  
**Durum:** ✅ Done

**Açıklama:**
Kullanıcının geçmiş siparişlerini listeleme.

**Checklist:**
- [x] `GET /v1/orders/my-history` endpoint
- [x] Auth required (JWT)
- [x] Pagination (page, limit params)
- [x] Filter by date range (start_date, end_date)
- [x] Filter by restaurant_id
- [x] Sort by declared_at DESC (en yeni önce)
- [x] Include restaurant bilgisi (JOIN)
- [x] Include order_items (nested)
- [x] Response: total count + paginated data

**Acceptance Criteria:**
- Sadece kendi siparişlerini görmeli (user_id filter)
- Empty result için boş array dönmeli
- Page 2, 3 düzgün çalışmalı

**Tamamlanma Notları:**
- OrderHistoryListResponse schema ile sayfalı response
- selectinload ile restaurant + items eager load
- Query params: page, limit, start_date, end_date, restaurant_id

**Dependencies:** TASK-BE-011

---

### 2.4 Risk Management

#### TASK-BE-013: Risky Restaurants Endpoint 🔴 P0
**Süre:** 3 saat  
**Gerçek Süre:** ~2 saat
**Sorumlu:** Emre  
**Durum:** ✅ Done

**Açıklama:**
Riskli restoranları listeleme (mobil ana sayfa için).

**Checklist:**
- [x] `GET /v1/restaurants/risky` endpoint
- [x] Filter: `risk_status IN ['WATCHLIST', 'RED_FLAG', 'BLACKLISTED']`
- [x] Order by: total_complaints DESC
- [ ] Include: last incident date (opsiyonel)
- [ ] Cache response (Redis, 5 dakika) (ileride)
- [x] Response: restaurant list

**Acceptance Criteria:**
- ✅ Sadece riskli restoranlar dönmeli
- ✅ SAFE restoranlar listelenmemeli
- Response <200ms (cached - ileride Redis ile)

**Tamamlanma Notları:**
- `GET /v1/restaurants/risky` endpoint implemente edildi
- WATCHLIST, RED_FLAG, BLACKLISTED filtreli
- Mobile home ekranına bağlandı

**Dependencies:** TASK-BE-004

---

#### TASK-BE-014: Risk Analysis Engine 🟡 P1
**Süre:** 6 saat  
**Sorumlu:** Emre  
**Durum:** ⏳ Pending

**Açıklama:**
Otomatik risk statüsü güncelleme algoritması.

**Checklist:**
- [ ] `app/services/risk_service.py` oluştur
- [ ] `update_restaurant_risk_status()` fonksiyonu
- [ ] Algoritma (SPEC'teki):
  - [ ] Son 24 saatte 3+ şikayet → RED_FLAG
  - [ ] Son 24 saatte 2 şikayet → WATCHLIST
  - [ ] Şikayet oranı >5% → WATCHLIST
  - [ ] Aksi halde → SAFE
- [ ] Database update (risk_status, risk_reason)
- [ ] Notification trigger (RED_FLAG ise)
- [ ] PostgreSQL NOTIFY/LISTEN (async queue)
- [ ] Cron job (her 1 saatte bir tüm restoranları check et)

**Acceptance Criteria:**
- Şikayet geldiğinde risk otomatik güncellenmeli
- RED_FLAG olduğunda bildirim gitmeli
- Manual risk update yapılabilmeli (admin için)

**Dependencies:** TASK-BE-015

---

#### TASK-BE-015: Health Incident Report Endpoint 🟡 P1
**Süre:** 4 saat  
**Gerçek Süre:** ~1.5 saat  
**Sorumlu:** Emre  
**Durum:** ✅ Done

**Açıklama:**
Öğrencinin sağlık sorunu bildirmesi.

**Checklist:**
- [x] `POST /v1/incidents/report` endpoint
- [x] Auth required (JWT)
- [x] Request: suspected_order_id, symptoms, severity_level
- [x] Validation: order öğrenciye ait mi?
- [x] HealthIncident kaydı oluştur
- [x] Restaurant total_complaints artır (trigger veya manual)
- [x] Risk service çağır (otomatik risk check)
- [ ] Yurt müdürüne bildirim (email - future)
- [x] Response: incident_id, next_steps

**Acceptance Criteria:**
- Postman'den test edilebilmeli
- Risk otomatik güncellenmeli (threshold geçerse)
- Başka öğrencinin siparişi için şikayet edilemez

**Tamamlanma Notları:**
- risk_service.py: Otomatik risk güncelleme (24s 3+ → RED_FLAG, 2 → WATCHLIST, oran %5 → WATCHLIST)
- Semptom min 10 karakter validasyonu
- severity_level 1-5 aralığı
- Ciddiyet >=4 için "acil servis" önerisi next_steps'te

**Dependencies:** TASK-BE-012

---

### 2.5 Admin Endpoints

#### TASK-BE-016: Admin Dashboard Statistics 🟡 P1
**Süre:** 5 saat  
**Gerçek Süre:** ~3 saat
**Sorumlu:** Emre  
**Durum:** ✅ Done

**Açıklama:**
Yurt müdürü dashboard için istatistikler.

**Checklist:**
- [x] `GET /v1/admin/dashboard/statistics` endpoint
- [ ] Auth required (role: DORM_MANAGER) (production'da eklenecek)
- [x] Query params: period (last_7_days, last_30_days)
- [x] Aggregation:
  - [x] Total orders (period içinde)
  - [x] Active students (sipariş veren)
  - [x] Total incidents
  - [x] Top 5 restaurants
  - [x] Incidents by restaurant
  - [x] Daily breakdown (chart için)
- [ ] PostgreSQL View (ileride performance için)
- [x] Cache (Redis, 10 dakika)

**Acceptance Criteria:**
- ✅ Response <500ms
- Chart.js ile görselleştirilebilir format (Admin panel entegre)

**Tamamlanma Notları:**
- Dashboard API Admin panel'e bağlandı
- Gerçek veri ile çalışıyor

**Dependencies:** TASK-BE-007

---

#### TASK-BE-017: Restaurant Risk Update (Manual) 🟡 P1
**Süre:** 3 saat  
**Gerçek Süre:** ~2 saat
**Sorumlu:** Emre  
**Durum:** ✅ Done

**Açıklama:**
Admin manuel olarak restoran risk statüsünü güncelleyebilir.

**Checklist:**
- [x] `PUT /v1/admin/restaurants/{id}/risk-status` endpoint
- [ ] Auth required (role: DORM_MANAGER) (production'da eklenecek)
- [x] Request: new_status, reason (Query params)
- [x] Validation: status ENUM'da olmalı
- [x] Database update
- [ ] Audit log (ileride)
- [ ] Notification trigger (RED_FLAG ise) (ileride)

**Acceptance Criteria:**
- ✅ Manual update çalışmalı
- Admin panel Restoranlar sayfasından risk güncelleme aktif

**Tamamlanma Notları:**
- Restoran risk durumu güncelleme Admin panel'e entegre

**Dependencies:** TASK-BE-014

---

### 2.6 Security & Performance

#### TASK-BE-018: Rate Limiting (Redis) 🟡 P1
**Süre:** 4 saat  
**Gerçek Süre:** ~1.5 saat  
**Sorumlu:** Emre  
**Durum:** ✅ Done

**Açıklama:**
API abuse koruması için rate limiting.

**Checklist:**
- [x] `slowapi` kütüphanesi
- [x] Redis backend (storage_uri)
- [x] Rate limits (SPEC'teki):
  - [x] `/auth/login`: 5 req/min
  - [x] `/auth/register`: 5 req/min
  - [x] `/orders/upload`: 10 req/hour
  - [x] `/incidents/report`: 3 req/hour
  - [x] Global: 100 req/min per IP
- [x] 429 Too Many Requests response
- [ ] Header'da limit bilgisi (FastAPI uyumluluk için headers_enabled=False)

**Acceptance Criteria:**
- Limit aşıldığında 429 dönmeli
- Redis'te counter tutulmalı
- Farklı endpoint'ler farklı limitlerde

**Tamamlanma Notları:**
- app/core/limiter.py: Limiter Redis + in_memory_fallback
- Login, Register, Upload, Report endpoint'lerine özel limitler
- Auth: request/body parametreleri slowapi uyumlu (request=Request, body=LoginRequest)
- Dockerfile: PyTorch CPU-only + pip cache (build hızlandırma)

**Dependencies:** TASK-BE-001

---

#### TASK-BE-019: Logging & Monitoring 🟢 P2
**Süre:** 3 saat  
**Gerçek Süre:** ~1 saat  
**Sorumlu:** Emre  
**Durum:** ✅ Done

**Açıklama:**
Structured logging ve Sentry entegrasyonu.

**Checklist:**
- [x] Loguru kütüphanesi setup
- [x] JSON structured logs (production file)
- [x] Log levels: DEBUG, INFO, WARNING, ERROR
- [x] Log rotation (max 100MB per file)
- [x] Sentry SDK initialize (SENTRY_DSN opsiyonel)
- [x] Error tracking (exception capture)
- [x] Performance monitoring (traces_sample_rate)
- [x] Request logging middleware (method, path, status, duration, ip)

**Acceptance Criteria:**
- Her request loglanmalı
- Error'lar Sentry'ye gitmeli (DSN varsa)
- Local'de console, production'da file

**Tamamlanma Notları:**
- app/core/logging_config.py: Loguru + InterceptHandler
- app/core/middleware.py: RequestLoggingMiddleware
- Production: logs/app.log JSON, rotation 100MB, 7 gün retention

**Dependencies:** TASK-BE-002

---

## 3. MOBILE TASKS

### 3.1 Project Setup

#### TASK-MB-001: Flutter Project Initialize 🔴 P0
**Süre:** 2 saat  
**Gerçek Süre:** 0.5 saat
**Sorumlu:** Mehmet  
**Durum:** ✅ Done

**Açıklama:**
Flutter projesini oluştur ve temel yapılandırma.

**Checklist:**
- [x] `flutter create mobile` çalıştır
- [x] Klasör yapısını organize et (SPEC'e göre):
  - [x] `lib/core/` - Constants, themes, utils
  - [x] `lib/features/` - Feature-first yapı
  - [x] `lib/features/auth/`
  - [x] `lib/features/home/`
  - [x] `lib/features/order/`
  - [x] `lib/features/profile/`
- [x] Package name: `tr.gov.gidanobeti`
- [ ] `pubspec.yaml` - Dependencies ekle (SPEC'teki) - Sonraki task
- [ ] App icon oluştur (Android + iOS) - Sonraki task
- [ ] Splash screen setup - Sonraki task

**Acceptance Criteria:**
- ✅ `flutter run` çalışmalı
- ✅ Hot reload çalışmalı
- ✅ iOS + Android build alınabilmeli

**Tamamlanma Notları:**
- Flutter projesi başarıyla oluşturuldu
- Organization identifier: tr.gov.gidanobeti
- Clean Architecture klasör yapısı (lib/core, lib/features)
- README.md güncellendi
- AppConstants oluşturuldu
- 130 dosya oluşturuldu

**Dependencies:** Yok

---

#### TASK-MB-002: State Management (Bloc) Setup 🔴 P0
**Süre:** 3 saat  
**Sorumlu:** Mehmet  
**Durum:** ✅ Done  
**Gerçek Süre:** 1 saat

**Açıklama:**
BLoC pattern kurulumu ve temel yapı.

**Checklist:**
- [x] `flutter_bloc` dependency ekle (v8.1.6)
- [x] `equatable` dependency ekle (v2.0.8)
- [x] `logger` dependency ekle (v2.6.2)
- [x] `lib/core/bloc/` klasörü oluştur
- [x] Base state sınıfı (BaseBlocState with Equatable)
- [x] Base event sınıfı (BaseBlocEvent with Equatable)
- [x] AppBlocObserver (debug logging: onCreate, onEvent, onTransition, onError, onClose)
- [x] MultiBlocProvider setup (main.dart - yorum olarak eklendi)
- [x] Bloc.observer = AppBlocObserver() (main.dart)

**Tamamlanan Dosyalar:**
- `lib/core/bloc/base_bloc_state.dart` (abstract class with Equatable)
- `lib/core/bloc/base_bloc_event.dart` (abstract class with Equatable)
- `lib/core/bloc/app_bloc_observer.dart` (emoji + renkli logging)
- `lib/main.dart` (BLoC observer setup + MaterialApp configuration)
- `pubspec.yaml` (13 runtime + 3 dev dependencies)

**Acceptance Criteria:**
- ✅ BLoC pattern hazır
- ✅ State değişiklikleri console'da görünecek (AppBlocObserver)
- ✅ Equatable ile verimli state comparison

**Not:** Windows Developer Mode requirement var (symlink için). Android emulator veya gerçek cihaz ile test edilecek.

**Dependencies:** TASK-MB-001

---

#### TASK-MB-003: API Client (Dio + Retrofit) 🔴 P0
**Süre:** 4 saat  
**Sorumlu:** Mehmet  
**Durum:** ⏳ Pending

**Açıklama:**
Backend API ile iletişim için HTTP client.

**Checklist:**
- [ ] `lib/core/api/` klasörü oluştur
- [ ] Dio instance oluştur
- [ ] Base URL config (dev vs prod)
- [ ] Interceptors:
  - [ ] Auth interceptor (JWT token header'a ekle)
  - [ ] Logging interceptor (debug için)
  - [ ] Error interceptor (401 → logout)
- [ ] Retrofit interface: `api_service.dart`
  - [ ] `@POST('/v1/auth/login')`
  - [ ] `@POST('/v1/auth/register')`
  - [ ] `@POST('/v1/orders/upload')`
  - [ ] `@GET('/v1/restaurants/risky')`
- [ ] JSON serialization (json_serializable)

**Acceptance Criteria:**
- Backend'e istek atılabilmeli
- JWT token otomatik eklenmeli
- Network error handling çalışmalı

**Dependencies:** TASK-MB-002, TASK-BE-006

---

### 3.2 Authentication Feature

#### TASK-MB-004: Login Screen UI 🔴 P0
**Süre:** 4 saat  
**Sorumlu:** Mehmet  
**Durum:** ⏳ Pending

**Açıklama:**
Giriş ekranı tasarımı ve implementasyonu.

**Checklist:**
- [ ] `lib/features/auth/presentation/pages/login_page.dart`
- [ ] TCKN input (11 haneli, numeric keyboard)
- [ ] Şifre input (obscure text, toggle visibility)
- [ ] "Giriş Yap" butonu
- [ ] "Hesabın yok mu? Kayıt Ol" linki
- [ ] Loading indicator (login sırasında)
- [ ] Error mesajı gösterimi (SnackBar/Dialog)
- [ ] Form validation (boş alan kontrolü)
- [ ] Responsive design (tablet desteği)

**Acceptance Criteria:**
- Design mockup'a uygun olmalı
- Klavye açıldığında UI bozulmamalı
- Figma'daki renkler/fontlar kullanılmalı

**Dependencies:** TASK-MB-003

---

#### TASK-MB-005: Register Screen UI 🔴 P0
**Süre:** 4 saat  
**Sorumlu:** Mehmet  
**Durum:** ⏳ Pending

**Açıklama:**
Kayıt ekranı tasarımı.

**Checklist:**
- [ ] `lib/features/auth/presentation/pages/register_page.dart`
- [ ] Form fields:
  - [ ] TCKN (11 haneli)
  - [ ] Ad Soyad
  - [ ] Email
  - [ ] Telefon (optional)
  - [ ] Yurt seçimi (Dropdown)
  - [ ] Oda numarası
  - [ ] Şifre
  - [ ] Şifre tekrar
- [ ] Form validation (frontend)
- [ ] Şifre strength indicator
- [ ] "Kayıt Ol" butonu
- [ ] KVKK onayı checkbox

**Acceptance Criteria:**
- Tüm alanlar doğru validate edilmeli
- Şifre match kontrolü
- Backend'e istek atılmalı

**Dependencies:** TASK-MB-004

---

#### TASK-MB-006: Auth Bloc (Logic) 🔴 P0
**Süre:** 5 saat  
**Sorumlu:** Mehmet  
**Durum:** ⏳ Pending

**Açıklama:**
Authentication business logic.

**Checklist:**
- [ ] `lib/features/auth/bloc/auth_bloc.dart`
- [ ] Events:
  - [ ] `AuthLoginRequested`
  - [ ] `AuthRegisterRequested`
  - [ ] `AuthLogoutRequested`
  - [ ] `AuthCheckRequested` (app start)
- [ ] States:
  - [ ] `AuthInitial`
  - [ ] `AuthLoading`
  - [ ] `AuthAuthenticated`
  - [ ] `AuthUnauthenticated`
  - [ ] `AuthError`
- [ ] JWT token storage (flutter_secure_storage)
- [ ] Token persistence (app restart sonrası)
- [ ] Logout (token sil)

**Acceptance Criteria:**
- Login success → `AuthAuthenticated` state
- Token persist edilmeli (app kapatıp açınca login kalmalı)
- Logout çalışmalı

**Dependencies:** TASK-MB-003

---

### 3.3 Home Feature (Risk Dashboard)

#### TASK-MB-007: Home Screen UI 🔴 P0
**Süre:** 6 saat  
**Sorumlu:** Mehmet  
**Durum:** ⏳ Pending

**Açıklama:**
Ana sayfa - Risk panosu.

**Checklist:**
- [ ] `lib/features/home/presentation/pages/home_page.dart`
- [ ] App bar (logo, profil ikonu)
- [ ] Hoşgeldin mesajı (kullanıcı adı)
- [ ] **Risk Panosu** (Ana özellik):
  - [ ] "Riskli Restoranlar" başlığı
  - [ ] Liste (eğer varsa):
    - [ ] Restoran ismi
    - [ ] Risk badge (RED_FLAG: kırmızı, WATCHLIST: sarı)
    - [ ] Alert mesajı
  - [ ] Empty state (hiç riskli restoran yoksa)
- [ ] "Sipariş Yükle" butonu (FAB - Floating Action Button)
- [ ] Bottom navigation bar
- [ ] Pull-to-refresh

**Acceptance Criteria:**
- Backend'den riskli restoranlar çekilmeli
- RED_FLAG restoranlar belirgin gösterilmeli
- Empty state güzel görünmeli
- Refresh çalışmalı

**Dependencies:** TASK-MB-006, TASK-BE-013

---

#### TASK-MB-008: Home Bloc (Logic) 🟡 P1
**Süre:** 3 saat  
**Sorumlu:** Mehmet  
**Durum:** ⏳ Pending

**Açıklama:**
Ana sayfa business logic.

**Checklist:**
- [ ] `lib/features/home/bloc/home_bloc.dart`
- [ ] Events:
  - [ ] `HomeFetchRiskyRestaurants`
  - [ ] `HomeRefresh`
- [ ] States:
  - [ ] `HomeLoading`
  - [ ] `HomeLoaded` (restaurant listesi)
  - [ ] `HomeError`
- [ ] API call: `GET /restaurants/risky`
- [ ] Error handling (network error, timeout)

**Acceptance Criteria:**
- Sayfa açıldığında otomatik yüklenmeli
- Refresh çalışmalı
- Error state gösterilmeli

**Dependencies:** TASK-MB-007

---

### 3.4 Order Upload Feature

#### TASK-MB-009: Order Upload Screen UI 🔴 P0
**Süre:** 6 saat  
**Sorumlu:** Mehmet  
**Durum:** ⏳ Pending

**Açıklama:**
Sipariş yükleme ekranı (kamera/galeri).

**Checklist:**
- [ ] `lib/features/order/presentation/pages/order_upload_page.dart`
- [ ] Kamera butonu
- [ ] Galeri butonu
- [ ] Seçilen görseli önizleme
- [ ] Kırp/döndür seçenekleri (image_cropper)
- [ ] Manuel not ekleme (TextArea - optional)
- [ ] "Yükle" butonu
- [ ] Upload progress indicator (CircularProgressIndicator)
- [ ] Success dialog (OCR sonucu göster)
- [ ] Risk warning dialog (RED_FLAG restoran)

**Acceptance Criteria:**
- Kamera ve galeri çalışmalı (permission)
- Görsel önizlenebilmeli
- Upload progress gösterilmeli
- OCR sonucu ekranda çıkmalı

**Dependencies:** TASK-MB-006, TASK-BE-011

---

#### TASK-MB-010: Camera & Image Picker Integration 🔴 P0
**Süre:** 4 saat  
**Sorumlu:** Mehmet  
**Durum:** ⏳ Pending

**Açıklama:**
Kamera ve galeri erişimi.

**Checklist:**
- [ ] `image_picker` package setup
- [ ] Permission handling:
  - [ ] Android: AndroidManifest.xml (CAMERA, READ_EXTERNAL_STORAGE)
  - [ ] iOS: Info.plist (NSCameraUsageDescription)
- [ ] Pick from camera
- [ ] Pick from gallery
- [ ] Image compression (max 5MB)
- [ ] HEIC to JPEG conversion (iOS)

**Acceptance Criteria:**
- Permission dialog görünmeli
- iOS HEIC görseller desteklenmeli
- Büyük görseller compress edilmeli

**Dependencies:** TASK-MB-009

---

#### TASK-MB-011: Order Upload Bloc 🔴 P0
**Süre:** 5 saat  
**Sorumlu:** Mehmet  
**Durum:** ⏳ Pending

**Açıklama:**
Sipariş yükleme business logic.

**Checklist:**
- [ ] `lib/features/order/bloc/order_upload_bloc.dart`
- [ ] Events:
  - [ ] `OrderUploadImageSelected` (görsel seçildi)
  - [ ] `OrderUploadSubmitted` (yükleme başlat)
- [ ] States:
  - [ ] `OrderUploadInitial`
  - [ ] `OrderUploadImageSelected` (preview)
  - [ ] `OrderUploadUploading` (progress: 0-100)
  - [ ] `OrderUploadSuccess` (OCR result)
  - [ ] `OrderUploadError`
- [ ] API call: `POST /orders/upload` (multipart)
- [ ] Upload progress tracking (Dio onSendProgress)

**Acceptance Criteria:**
- Multipart file upload çalışmalı
- Progress bar güncellenmeli
- Success/error state doğru işlenmeli

**Dependencies:** TASK-MB-010, TASK-BE-011

---

#### TASK-MB-012: Risk Warning Dialog 🟡 P1
**Süre:** 2 saat  
**Sorumlu:** Mehmet  
**Durum:** ⏳ Pending

**Açıklama:**
Riskli restoran uyarısı dialog.

**Checklist:**
- [ ] Custom dialog widget
- [ ] Kırmızı renk şeması (alert)
- [ ] Warning icon
- [ ] Mesaj: "⚠️ DİKKAT: Bu restoran denetim altında!"
- [ ] Risk reason göster
- [ ] "İade Destek Kartı" butonu (future)
- [ ] "Tamam" butonu

**Acceptance Criteria:**
- Backend'den warning gelirse otomatik açılmalı
- Design görsel olarak çarpıcı olmalı

**Dependencies:** TASK-MB-011

---

### 3.5 Profile & History

#### TASK-MB-013: Order History Screen 🟡 P1
**Süre:** 5 saat  
**Sorumlu:** Mehmet  
**Durum:** ⏳ Pending

**Açıklama:**
Geçmiş siparişler listesi.

**Checklist:**
- [ ] `lib/features/profile/presentation/pages/order_history_page.dart`
- [ ] Liste (Card widgets):
  - [ ] Restoran ismi
  - [ ] Tarih/saat
  - [ ] Toplam tutar
  - [ ] Risk badge (o zamanki durum)
- [ ] Pagination (infinite scroll)
- [ ] Pull-to-refresh
- [ ] Empty state (hiç sipariş yoksa)
- [ ] Filter by date (optional)

**Acceptance Criteria:**
- Backend'den history çekilmeli
- Pagination çalışmalı (scroll to bottom → load more)
- Refresh çalışmalı

**Dependencies:** TASK-MB-006, TASK-BE-012

---

#### TASK-MB-014: Profile Screen 🟢 P2
**Süre:** 3 saat  
**Sorumlu:** Mehmet  
**Durum:** ⏳ Pending

**Açıklama:**
Kullanıcı profili ve ayarlar.

**Checklist:**
- [ ] `lib/features/profile/presentation/pages/profile_page.dart`
- [ ] Kullanıcı bilgileri:
  - [ ] Avatar (placeholder)
  - [ ] Ad Soyad
  - [ ] Email
  - [ ] Yurt + Oda No
- [ ] Menü items:
  - [ ] Sipariş Geçmişi (navigation)
  - [ ] Bildirim Ayarları (future)
  - [ ] Hakkında
  - [ ] Çıkış Yap
- [ ] Logout confirmation dialog

**Acceptance Criteria:**
- Logout çalışmalı (token silinmeli)
- Sipariş geçmişine navigate edilmeli

**Dependencies:** TASK-MB-006

---

### 3.6 Incident Report

#### TASK-MB-015: Incident Report Screen 🟡 P1
**Süre:** 4 saat  
**Sorumlu:** Mehmet  
**Durum:** ⏳ Pending

**Açıklama:**
Sağlık sorunu bildirimi ekranı.

**Checklist:**
- [ ] `lib/features/incident/presentation/pages/report_incident_page.dart`
- [ ] Form:
  - [ ] Şüphelenilen sipariş seçimi (Dropdown - son 3 gün)
  - [ ] Semptomlar (TextArea)
  - [ ] Şiddet seviyesi (1-5 slider)
  - [ ] Başlangıç zamanı (DateTimePicker)
- [ ] "Bildir" butonu
- [ ] Success dialog
- [ ] Disclaimer: "Sağlık görevlisine başvurunuz"

**Acceptance Criteria:**
- Backend'e şikayet gönderilebilmeli
- Form validation çalışmalı
- Success mesajı gösterilmeli

**Dependencies:** TASK-MB-013, TASK-BE-015

---

### 3.7 Notifications

#### TASK-MB-016: Push Notification Setup (Firebase) 🟢 P2
**Süre:** 5 saat  
**Sorumlu:** Mehmet  
**Durum:** ⏳ Pending

**Açıklama:**
Push notification altyapısı.

**Checklist:**
- [ ] Firebase project oluştur
- [ ] Android: google-services.json ekle
- [ ] iOS: GoogleService-Info.plist ekle
- [ ] `firebase_messaging` package
- [ ] FCM token al (device registration)
- [ ] Token'ı backend'e gönder (future endpoint)
- [ ] Foreground notification handler
- [ ] Background notification handler
- [ ] Notification tap → navigation

**Acceptance Criteria:**
- Test notification alınabilmeli (Firebase Console)
- Foreground + background çalışmalı
- Notification tap ile doğru sayfaya gitmeli

**Dependencies:** TASK-MB-006

**Not:** Backend notification endpoint (future task)

---

## 4. ADMIN PANEL TASKS

### 4.1 Setup

#### TASK-AD-001: Next.js Project Setup 🟡 P1
**Süre:** 3 saat  
**Gerçek Süre:** 1 saat
**Sorumlu:** Emre  
**Durum:** ✅ Done

**Açıklama:**
Next.js admin panel kurulumu.

**Checklist:**
- [x] `npx create-next-app admin-panel --typescript`
- [x] Folder structure:
  - [x] `app/` - Pages (App Router)
  - [x] `components/` - Reusable components
  - [x] `lib/` - API client, utils
- [x] Dependencies:
  - [x] `axios` (API client)
  - [x] `chart.js` + `react-chartjs-2` (charts)
  - [x] `swr` (data fetching)
  - [x] `tailwindcss` (styling)
  - [x] `lucide-react` (icons)
- [x] Environment variables (.env.local)
- [x] ESLint + TypeScript

**Tamamlanma Notları:**
- Next.js 16 + TypeScript + TailwindCSS kuruldu
- lib/api-client.ts: Axios instance + JWT interceptor
- lib/auth.ts: Token management utilities
- components/ui/: Card, Button, Input, Badge components
- .env.local: API_URL configuration

**Acceptance Criteria:**
- ✅ `npm run dev` çalışmalı
- ✅ TypeScript errors olmamalı
- ✅ http://localhost:3000 açılıyor

**Dependencies:** Yok

---

### 4.2 Dashboard

#### TASK-AD-002: Admin Login Page 🟡 P1
**Süre:** 3 saat  
**Gerçek Süre:** 0.5 saat
**Sorumlu:** Emre  
**Durum:** ✅ Done

**Açıklama:**
Admin giriş sayfası.

**Checklist:**
- [x] `app/login/page.tsx` oluşturuldu
- [x] Form: TCKN + Password
- [x] Login API call hazır (backend endpoint bekliyor)
- [x] JWT token storage (localStorage)
- [x] Redirect to dashboard
- [x] Error handling + loading state
- [x] Role kontrolü (DORM_MANAGER/SYS_ADMIN)

**Tamamlanma Notları:**
- Modern gradient background + card design
- Form validation
- API error handling
- Responsive design

**Acceptance Criteria:**
- ✅ Login formu çalışıyor (UI hazır)
- ✅ Token kaydediliyor
- ✅ Error mesajları gösteriliyor
- ⏸️ Backend endpoint bekleniyor

**Dependencies:** TASK-AD-001, [TASK-BE-006 - Beklemede]

---

#### TASK-AD-003: Dashboard Page (Statistics) 🟡 P1
**Süre:** 6 saat  
**Gerçek Süre:** 1 saat
**Sorumlu:** Emre  
**Durum:** ✅ Done

**Açıklama:**
Ana dashboard - istatistikler ve grafikler.

**Checklist:**
- [x] `app/dashboard/page.tsx` oluşturuldu
- [x] `app/dashboard/layout.tsx` - Sidebar + navigation (suppressHydrationWarning eklendi)
- [x] KPI Cards:
  - [x] Toplam Sipariş (son 7 gün)
  - [x] Aktif Öğrenci
  - [x] Toplam Vaka
  - [x] Risk Altındaki Restoran
- [x] Chart placeholders (Chart.js entegrasyonu hazır)
- [x] Authentication check (localStorage 'token' key ile)
- [x] Logout functionality
- [x] Responsive design
- [x] Token key consistency (auth.ts + api-client.ts + login.tsx)
- [ ] Date range picker (ileride)
- [ ] Gerçek API call (backend ready olunca)

**Tamamlanma Notları:**
- 4 KPI card + icon'lar (Lucide React)
- Sidebar navigation (Dashboard, Restoranlar, Siparişler, Vakalar)
- Chart placeholder'lar hazır
- Mock data ile çalışıyor
- Professional UI/UX
- Hydration uyarıları düzeltildi (DarkReader uyumlu)
- Token yönetimi standardize edildi (localStorage 'token' key)
- Fully functional authentication flow

**Acceptance Criteria:**
- ✅ Dashboard açılıyor ve görünüyor
- ✅ Sidebar navigation çalışıyor
- ✅ Logout butonu çalışıyor
- ✅ Responsive (mobile + desktop)
- ✅ Token authentication çalışıyor (mock)
- ✅ Hydration warnings çözüldü
- ⏸️ Gerçek data backend'den gelecek (TASK-BE-016)

**Dependencies:** TASK-AD-002, TASK-BE-016

---

#### TASK-AD-004: Restaurants Management Page 🟡 P1
**Süre:** 5 saat  
**Gerçek Süre:** 1 saat
**Sorumlu:** Emre  
**Durum:** ✅ Done

**Açıklama:**
Restoran listesi ve risk yönetimi.

**Checklist:**
- [x] `app/dashboard/restaurants/page.tsx` oluşturuldu
- [x] DataTable:
  - [x] Restoran ismi
  - [x] Risk durumu (badge - 4 renk)
  - [x] Toplam sipariş
  - [x] Toplam şikayet
  - [x] Aksiyonlar (Edit butonu)
- [x] Search/Filter (restoran ismi)
- [x] Sort by (şikayet sayısı, risk durumu, isim)
- [x] Edit Modal:
  - [x] Risk statü dropdown (4 durum)
  - [x] Risk nedeni (textarea)
  - [x] Kaydet butonu
- [x] Stats cards (5 adet - toplam, güvenli, izlemede, riskli, yasaklı)
- [x] Mock data (5 restoran örneği)
- [x] Sidebar active state (mavi highlight)
- [x] API calls:
  - [x] `GET /restaurants` (liste)
  - [x] `PUT /admin/restaurants/{id}/risk-status`

**Tamamlanma Notları:**
- Responsive table design
- Color-coded risk badges (yeşil/sarı/kırmızı/siyah)
- Real-time search & filter
- Professional modal design
- Empty state handling
- Mock data ile tam fonksiyonel

**Acceptance Criteria:**
- ✅ Tablo düzgün çalışıyor
- ✅ Risk statü güncellenebiliyor (mock)
- ✅ Arama ve filtreleme çalışıyor
- ✅ Sidebar active state gösteriliyor
- ✅ Backend API entegre

**Dependencies:** TASK-AD-002, TASK-BE-017

---

#### TASK-AD-005: Orders List Page 🟢 P2
**Süre:** 4 saat  
**Gerçek Süre:** 1 saat
**Sorumlu:** Emre  
**Durum:** ✅ Done

**Açıklama:**
Tüm siparişleri görme ve arama.

**Checklist:**
- [x] `app/dashboard/orders/page.tsx` oluşturuldu
- [x] DataTable:
  - [x] Öğrenci adı
  - [x] Restoran
  - [x] Tarih/saat
  - [x] Tutar
  - [x] Method (Ekran Görüntüsü/Fiş badge)
- [x] Search (öğrenci ismi, restoran)
- [x] Filter:
  - [x] Date range (başlangıç-bitiş)
  - [x] Restaurant dropdown
  - [x] Method dropdown
- [x] Pagination (10 item/sayfa)
- [x] Export CSV butonu (UTF-8 BOM)
- [x] Stats cards (4 adet)
- [x] Mock data (12 sipariş)
- [x] API: `GET /admin/orders` + sayfalama (Daha fazla yükle)

**Tamamlanma Notları:**
- Responsive table design
- Real-time search & multi-filter
- Functional pagination with page numbers
- CSV export with Turkish characters (UTF-8 BOM)
- Color-coded method badges
- Empty state handling
- Date range picker
- Mock data ile tam fonksiyonel

**Acceptance Criteria:**
- ✅ Arama çalışıyor (öğrenci + restoran)
- ✅ CSV export ediliyor (Türkçe karakter desteği)
- ✅ Pagination düzgün çalışıyor
- ✅ Tüm filtreler çalışıyor
- ✅ Backend API entegre

**Dependencies:** TASK-AD-002

---

#### TASK-AD-006: Incidents Management Page 🟢 P2
**Süre:** 4 saat  
**Sorumlu:** Emre  
**Durum:** ✅ Done

**Açıklama:**
Sağlık vakalarını görme ve yönetme.

**Checklist:**
- [x] `app/dashboard/incidents/page.tsx`
- [x] DataTable:
  - [x] Öğrenci adı
  - [x] Restoran
  - [x] Semptomlar
  - [x] Şiddet
  - [x] Durum (PENDING/INVESTIGATING/CONFIRMED/DISMISSED)
  - [x] Aksiyonlar
- [x] Detail Modal:
  - [x] Tüm bilgiler
  - [x] Admin notu ekleme
  - [x] Durum güncelleme
- [x] API:
  - [x] `GET /v1/admin/incidents`
  - [x] `PUT /v1/admin/incidents/{id}`

**Acceptance Criteria:**
- [x] Vakalar listelenebilmeli
- [x] Admin notu eklenebilmeli
- [x] Durum güncellenebilmeli

**Tamamlanma Notları:**
- Backend: admin.py list_incidents, update_incident
- Schemas: AdminIncidentListItem, AdminIncidentListResponse, AdminIncidentUpdateRequest
- Admin panel: sayfalama, filtre, modal

**Dependencies:** TASK-AD-002

---

## 5. DEVOPS & INFRASTRUCTURE

### 5.1 Deployment

#### TASK-DO-001: Production Server Setup 🟡 P1
**Süre:** 4 saat  
**Sorumlu:** Emre  
**Durum:** ⏳ Pending

**Açıklama:**
Production sunucusu kurulumu (DigitalOcean/AWS).

**Checklist:**
- [ ] Droplet/EC2 oluştur (Ubuntu 22.04 LTS)
- [ ] 4 CPU, 8GB RAM, 50GB SSD
- [ ] SSH key setup
- [ ] Firewall (UFW):
  - [ ] 22 (SSH)
  - [ ] 80 (HTTP)
  - [ ] 443 (HTTPS)
- [ ] Docker + Docker Compose kurulumu
- [ ] PostgreSQL backup script (cron)
- [ ] Fail2ban (SSH brute-force koruması)

**Acceptance Criteria:**
- SSH ile bağlanılabilmeli
- Docker çalışmalı
- Firewall aktif olmalı

**Dependencies:** Yok

---

#### TASK-DO-002: Domain & SSL Setup 🟡 P1
**Süre:** 2 saat  
**Sorumlu:** Emre  
**Durum:** ⏳ Pending

**Açıklama:**
Domain ve SSL sertifikası.

**Checklist:**
- [ ] Domain: api.gidanobeti.gov.tr (DNS A record)
- [ ] Certbot + Let's Encrypt kurulumu
- [ ] SSL sertifikası al (certbot --nginx)
- [ ] Auto-renewal (cron job)
- [ ] Test: https://api.gidanobeti.gov.tr/health

**Acceptance Criteria:**
- HTTPS bağlantısı çalışmalı
- SSL Labs A+ rating

**Dependencies:** TASK-DO-001

---

#### TASK-DO-003: Nginx Reverse Proxy 🟡 P1
**Süre:** 3 saat  
**Sorumlu:** Emre  
**Durum:** ⏳ Pending

**Açıklama:**
Nginx ile load balancing ve SSL termination.

**Checklist:**
- [ ] Nginx config dosyası:
  - [ ] Reverse proxy to FastAPI (port 8000)
  - [ ] SSL termination
  - [ ] Gzip compression
  - [ ] Rate limiting
  - [ ] Static file serving (future - admin panel)
- [ ] `/etc/nginx/sites-available/gidanobeti`
- [ ] Symlink to sites-enabled
- [ ] `nginx -t` (config test)
- [ ] `systemctl reload nginx`

**Acceptance Criteria:**
- API'ye nginx üzerinden erişilebilmeli
- SSL çalışmalı
- Gzip compression aktif olmalı

**Dependencies:** TASK-DO-002

---

#### TASK-DO-004: CI/CD Pipeline (GitHub Actions) 🟢 P2
**Süre:** 5 saat  
**Sorumlu:** Emre  
**Durum:** ⏳ Pending

**Açıklama:**
Otomatik deploy pipeline.

**Checklist:**
- [ ] `.github/workflows/deploy.yml`
- [ ] Steps:
  - [ ] Run tests (pytest)
  - [ ] Build Docker image
  - [ ] Push to Docker Hub/Registry
  - [ ] SSH to server
  - [ ] Pull latest image
  - [ ] Docker Compose up (rolling update)
- [ ] Secrets:
  - [ ] SERVER_IP
  - [ ] SSH_KEY
  - [ ] DOCKER_HUB_TOKEN
- [ ] Trigger: Push to `main` branch

**Acceptance Criteria:**
- Push to main → otomatik deploy
- Test fail olursa deploy iptal edilmeli
- Zero-downtime deployment

**Dependencies:** TASK-DO-003

---

### 5.2 Monitoring

#### TASK-DO-005: Sentry Error Tracking 🟢 P2
**Süre:** 2 saat  
**Sorumlu:** Emre  
**Durum:** ⏳ Pending

**Açıklama:**
Hata takibi için Sentry entegrasyonu.

**Checklist:**
- [ ] Sentry hesabı oluştur (free tier)
- [ ] Backend: Sentry SDK setup
- [ ] Mobile: Sentry SDK (Flutter)
- [ ] Admin: Sentry SDK (Next.js)
- [ ] DSN config (environment variable)
- [ ] Test: Manuel error throw et

**Acceptance Criteria:**
- Error'lar Sentry dashboard'da görünmeli
- User context (user_id) loglanmalı
- Breadcrumbs çalışmalı

**Dependencies:** TASK-DO-001

---

#### TASK-DO-006: Database Backup Strategy 🟡 P1
**Süre:** 3 saat  
**Sorumlu:** Emre  
**Durum:** ⏳ Pending

**Açıklama:**
Otomatik veritabanı yedeği.

**Checklist:**
- [ ] Backup script (`backup.sh`):
  - [ ] `pg_dump` ile SQL dump
  - [ ] Gzip compression
  - [ ] S3/Backblaze upload
  - [ ] Retention: 30 gün
- [ ] Cron job (her gece 03:00)
- [ ] Slack/Email bildirimi (başarılı/başarısız)
- [ ] Restore test (manuel)

**Acceptance Criteria:**
- Günlük backup alınmalı
- 30 günden eski backup'lar silinmeli
- Restore test başarılı olmalı

**Dependencies:** TASK-DO-001

---

## 6. TESTING & QA

### 6.1 Backend Tests

#### TASK-QA-001: Unit Tests (Backend) 🟡 P1
**Süre:** 8 saat  
**Sorumlu:** Mehmet  
**Durum:** 🚧 In Progress

**Açıklama:**
Backend için unit testler (pytest).

**Checklist:**
- [x] `tests/` klasör yapısı
- [x] Test fixtures (async_client, db_session, sample_receipt)
- [x] Test cases:
  - [x] Auth: Login (success, wrong password, invalid TCKN)
  - [x] Parser: parse_receipt_text (restoran, tutar, tarih, ürünler)
  - [x] Risk: update_restaurant_risk_status (SAFE, RED_FLAG, WATCHLIST)
  - [x] API: Health, Root endpoint
- [x] Coverage report (`pytest --cov`)
- [ ] Target: %80 coverage (şu an %65)

**Acceptance Criteria:**
- [x] Tüm testler pass olmalı (18/18 ✅)
- [ ] Coverage %80+
- [ ] CI/CD pipeline'da çalışmalı

**Tamamlanma Notları:**
- 18 test: test_api (5), test_parser (11), test_risk_service (3)
- pytest.ini, conftest.py, event_loop fixture
- Docker: `docker exec gidanobeti_api pytest tests/ -v --cov=app`

**Dependencies:** TASK-BE-006, TASK-BE-011

---

#### TASK-QA-002: Integration Tests (API) 🟡 P1
**Süre:** 6 saat  
**Sorumlu:** Mehmet  
**Durum:** ⏳ Pending

**Açıklama:**
API endpoint entegrasyon testleri.

**Checklist:**
- [ ] Postman collection oluştur
- [ ] Test scenaryo'ları:
  - [ ] User registration → Login → Order upload → History
  - [ ] Risk workflow: Incident report → Risk update → Alert
  - [ ] Admin: Dashboard stats, Restaurant update
- [ ] Newman (CLI runner) ile otomatik test
- [ ] CI/CD entegrasyonu

**Acceptance Criteria:**
- Tüm end-to-end flow'lar çalışmalı
- Postman collection exported (JSON)

**Dependencies:** TASK-BE-011, TASK-BE-015

---

### 6.2 Mobile Tests

#### TASK-QA-003: Widget Tests (Flutter) 🟢 P2
**Süre:** 6 saat  
**Sorumlu:** Mehmet  
**Durum:** ⏳ Pending

**Açıklama:**
Flutter widget testleri.

**Checklist:**
- [ ] `test/` klasörü
- [ ] Test cases:
  - [ ] Login form validation
  - [ ] Order upload UI
  - [ ] Risk warning dialog
- [ ] Mock API responses
- [ ] Coverage report

**Acceptance Criteria:**
- Widget tests pass olmalı
- Coverage %70+

**Dependencies:** TASK-MB-011

---

### 6.3 Performance & Security

#### TASK-QA-004: Load Testing (Locust) 🟡 P1
**Süre:** 4 saat  
**Sorumlu:** Emre  
**Durum:** ⏳ Pending

**Açıklama:**
Performance ve ölçeklenebilirlik testi.

**Checklist:**
- [ ] Locust script (`locustfile.py`)
- [ ] Test scenarios:
  - [ ] Login (100 concurrent users)
  - [ ] Order upload (50 concurrent uploads)
  - [ ] Dashboard stats (200 req/sec)
- [ ] Metrics:
  - [ ] Response time (p95, p99)
  - [ ] Error rate
  - [ ] Throughput
- [ ] Report: HTML + CSV

**Acceptance Criteria:**
- 500 concurrent user desteği
- Upload response time <5s (p95)
- Error rate <%5

**Dependencies:** TASK-BE-011, TASK-DO-001

---

#### TASK-QA-005: Security Audit (OWASP ZAP) 🟡 P1
**Süre:** 4 saat  
**Sorumlu:** Emre  
**Durum:** ⏳ Pending

**Açıklama:**
Güvenlik açığı taraması.

**Checklist:**
- [ ] OWASP ZAP kurulumu
- [ ] API'yi tara (automated scan)
- [ ] Vulnerability raporu al
- [ ] Critical/High severity düzelt
- [ ] OWASP Top 10 kontrolü:
  - [ ] SQL Injection
  - [ ] XSS
  - [ ] Broken Authentication
  - [ ] Insecure Direct Object Reference

**Acceptance Criteria:**
- Hiçbir critical vulnerability olmamalı
- OWASP raporu oluşturulmalı

**Dependencies:** TASK-BE-011

---

## 7. DOCUMENTATION

#### TASK-DOC-001: API Documentation (Swagger) 🟢 P2
**Süre:** 2 saat  
**Sorumlu:** Emre  
**Durum:** ⏳ Pending

**Açıklama:**
API dokümantasyonu Swagger UI'da.

**Checklist:**
- [ ] FastAPI otomatik docs iyileştir
- [ ] Her endpoint için:
  - [ ] Description
  - [ ] Request/Response examples
  - [ ] Error responses
- [ ] Authentication dokümantasyonu
- [ ] Postman collection export

**Acceptance Criteria:**
- `/docs` fully documented
- Examples doğru çalışmalı

**Dependencies:** TASK-BE-011

---

#### TASK-DOC-002: User Manual (Öğrenci) 🟢 P2
**Süre:** 3 saat  
**Sorumlu:** Mehmet  
**Durum:** ⏳ Pending

**Açıklama:**
Öğrenciler için kullanım kılavuzu.

**Checklist:**
- [ ] PDF döküman (Türkçe)
- [ ] Adımlar:
  - [ ] Kayıt olma
  - [ ] Sipariş yükleme
  - [ ] Risk uyarısı ne anlama gelir?
  - [ ] Şikayet bildirme
- [ ] Screenshot'lar (uygulama ekranları)

**Acceptance Criteria:**
- Basit ve anlaşılır dil
- Görseller güncel olmalı

**Dependencies:** TASK-MB-011

---

#### TASK-DOC-003: Admin Manual (Yurt Müdürü) 🟢 P2
**Süre:** 3 saat  
**Sorumlu:** Emre  
**Durum:** ⏳ Pending

**Açıklama:**
Yurt müdürü için yönetici kılavuzu.

**Checklist:**
- [ ] PDF döküman (Türkçe)
- [ ] Adımlar:
  - [ ] Giriş yapma
  - [ ] Dashboard okuma
  - [ ] Restoran risk güncelleme
  - [ ] Vaka yönetimi
- [ ] Screenshot'lar

**Acceptance Criteria:**
- Tüm özellikler açıklanmış olmalı

**Dependencies:** TASK-AD-006

---

## 8. GÖREV ÖNCELİK SIRASI (CRITICAL PATH)

### Hafta 1 (21-27 Ocak)
```
P0 - Critical (Paralel çalışılabilir)
├── TASK-BE-001: Docker Setup (Emre - 4h)
├── TASK-BE-002: FastAPI Scaffold (Emre - 3h)
├── TASK-BE-003: DB Models (Emre - 6h)
├── TASK-BE-004: Alembic (Emre - 3h)
├── TASK-BE-008: OCR Integration ✅
├── TASK-BE-009: OCR Parsing ✅
├── TASK-BE-010: Restaurant Matching ✅
└── TASK-BE-011: Order Upload Endpoint ✅
```

### Hafta 2 (28 Ocak - 3 Şubat)
```
P0 - Critical
├── TASK-BE-005: Register Endpoint (Emre - 4h)
├── TASK-BE-006: Login Endpoint (Emre - 4h)
├── TASK-BE-007: JWT Middleware (Emre - 3h)
├── TASK-BE-010: Restaurant Matching (Emre - 4h)
└── TASK-BE-011: Order Upload Endpoint (Emre+Mehmet - 6h) ⭐ EN ÖNEMLİ
```

### Hafta 3-4 (4-17 Şubat) - Mobile
```
P0 - Mobile MVP
├── TASK-MB-001→006: Auth Feature (Mehmet - 20h)
├── TASK-MB-007→008: Home Feature (Mehmet - 9h)
└── TASK-MB-009→012: Order Upload (Mehmet - 17h) ⚠️
```

**Not:** Tüm detaylı task listesi için PLAN.md'deki sprint breakdownlara bakılabilir.

---

## 9. TASK TRACKING

### Durum Güncellemeleri
Bu dosya **yaşayan bir döküman**dır. Her task tamamlandığında:
1. Durum güncelle (⏳ → ✅)
2. Actual süreyi not et (estimate vs actual)
3. Blocker varsa belirt
4. Git commit message: `[TASK-BE-001] Docker Setup completed`

### Weekly Report Template
```markdown
## Hafta X Raporu (Tarih)

### ✅ Tamamlanan Taskler
- [TASK-BE-001] Docker Setup (4h → 3.5h actual)
- [TASK-BE-002] FastAPI Scaffold (3h → 4h actual)

### 🚧 Devam Eden
- [TASK-BE-014] Risk Analysis Engine (TASK-BE-015 ile kısmen karşılandı)

### ✅ Tamamlanan (8 Şubat)
- TASK-BE-007: JWT Middleware & Permissions
- TASK-BE-018: Rate Limiting (Redis)
- TASK-BE-019: Logging & Monitoring

### ✅ Tamamlanan (4 Şubat)
- TASK-BE-012: Order History Endpoint
- TASK-BE-015: Health Incident Report Endpoint

### ✅ Tamamlanan (3 Şubat)
- TASK-BE-008: OCR Integration
- TASK-BE-009: OCR Parsing
- TASK-BE-010: Restaurant Matching
- TASK-BE-011: Order Upload Endpoint

### ❌ Blocker
- Yok

### 📊 Sprint Velocity
- Planlanan: 40 saat
- Gerçekleşen: 35 saat
- Efficiency: 87.5%

### 📅 Gelecek Hafta Hedefi
- Backend MVP tamamlanacak (BE-011)
```

---

## 10. İLETİŞİM & COLLABORATION

### Task Assignment
- **GitHub Issues** kullanılacak
- Her task bir issue olacak
- Labels: `backend`, `mobile`, `admin`, `bug`, `enhancement`
- Assignee: Sorumlu kişi
- Milestone: Sprint numarası

### Daily Standup Format
```
Dün ne yaptım?
- [TASK-BE-001] Docker setup tamamlandı

Bugün ne yapacağım?
- [TASK-BE-002] FastAPI scaffold başlayacağım

Blocker var mı?
- Yok / Var: [açıklama]
```

---

**Toplam Task Sayısı:** 60+  
**Toplam Estimated Effort:** ~350 saat  
**Gerçekçi Timeline:** 8 hafta (2 kişi)

---

**Son Güncelleme:** 21 Ocak 2026  
**Hazırlayan:** Mehmet Emre Kayacan & Mehmet Kurt  
**Durum:** ✅ Başlamaya Hazır

---

_"Task listesi detaylı ama gerçekçi. Her task SMART (Specific, Measurable, Achievable, Relevant, Time-bound). Şimdi kod yazmaya başlayabiliriz!"_ 🚀
