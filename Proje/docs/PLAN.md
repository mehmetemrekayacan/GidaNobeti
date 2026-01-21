# 📅 GIDA NÖBETİ - PROJE GELİŞTİRME PLANI

**Proje:** Gıda Nöbeti | Yurt Gıda Güvenliği Platformu  
**Başlangıç:** 21 Ocak 2026  
**Hedef Pilot Teslim:** 15 Mart 2026 (8 hafta)  
**Tam Deployment:** 1 Haziran 2026  
**Takım:** Mehmet Emre Kayacan & Mehmet Kurt

---

## 📋 İÇİNDEKİLER

1. [Proje Fazları](#1-proje-fazları)
2. [Sprint Planlaması](#2-sprint-planlaması)
3. [Milestone'lar](#3-milestonelar)
4. [Risk Yönetimi](#4-risk-yönetimi)
5. [Kaynak Dağılımı](#5-kaynak-dağılımı)
6. [Test Stratejisi](#6-test-stratejisi)
7. [Deployment Stratejisi](#7-deployment-stratejisi)

---

## 1. PROJE FAZLARI

### Faz 1: Altyapı ve Backend (2 hafta) ✅ Öncelik
**21 Ocak - 3 Şubat 2026**

#### Hedefler:
- ✅ Backend API temelinin kurulması
- ✅ Veritabanı şemasının oluşturulması
- ✅ OCR motor entegrasyonunun tamamlanması
- ✅ Authentication sisteminin çalışır hale getirilmesi

#### Deliverables:
- [ ] Çalışan FastAPI backend (Docker containerized)
- [ ] PostgreSQL veritabanı (migrations ile)
- [ ] OCR servis (test edilmiş, Türkçe fiş okuyabiliyor)
- [ ] JWT authentication + role-based access
- [ ] Swagger API dokümantasyonu (otomatik)

#### Critical Path:
```
Gün 1-2  : Docker + PostgreSQL + Backend scaffold
Gün 3-4  : Database models + Alembic migrations
Gün 5-7  : OCR motor test (EasyOCR + PaddleOCR)
Gün 8-9  : Authentication (register/login)
Gün 10-12: Order upload endpoint (OCR + DB save)
Gün 13-14: Testing + Bug fixes
```

---

### Faz 2: Mobile App (UI/UX) (2 hafta)
**4 Şubat - 17 Şubat 2026**

#### Hedefler:
- ✅ Flutter projesi kurulumu ve state management
- ✅ Öğrenci arayüzünün temel ekranları
- ✅ Kamera/galeri entegrasyonu
- ✅ API entegrasyonu (login + upload)

#### Deliverables:
- [ ] Login/Register ekranları (çalışır)
- [ ] Ana sayfa (Risk panosu)
- [ ] Sipariş yükleme ekranı (kamera + galeri)
- [ ] Geçmiş siparişler ekranı
- [ ] Push notification altyapısı (Firebase)

#### Ekranlar (Öncelik Sırasına Göre):
1. **Splash Screen** (1 gün)
2. **Login/Register** (2 gün)
3. **Home (Risk Dashboard)** (3 gün) - KRİTİK
4. **Order Upload (Kamera)** (3 gün) - KRİTİK
5. **Order History** (2 gün)
6. **Profile & Settings** (1 gün)
7. **Incident Report** (2 gün)

---

### Faz 3: Admin Dashboard (Web) (1.5 hafta)
**18 Şubat - 27 Şubat 2026**

#### Hedefler:
- ✅ Yurt müdürü için web paneli
- ✅ Dashboard istatistikleri (günlük, haftalık)
- ✅ Restoran risk yönetimi (manuel güncelleme)
- ✅ Öğrenci ve sipariş arama

#### Deliverables:
- [ ] Next.js/React admin panel (responsive)
- [ ] Dashboard (chart.js ile grafikler)
- [ ] Restoran yönetim sayfası
- [ ] Vaka (incident) yönetim sayfası
- [ ] CSV export (raporlar için)

#### Sayfalar:
1. **Dashboard** - İstatistikler
2. **Restaurants** - Risk statü güncelleme
3. **Orders** - Tüm siparişleri görme
4. **Students** - Öğrenci listesi
5. **Incidents** - Şikayetler & Takip

---

### Faz 4: Entegrasyon ve Test (1 hafta)
**28 Şubat - 6 Mart 2026**

#### Hedefler:
- ✅ Tüm modüllerin birlikte çalışması
- ✅ End-to-end test senaryoları
- ✅ Performance testing (load testing)
- ✅ Security audit (penetration testing)

#### Test Senaryoları:
1. **Öğrenci Journey**:
   - Kayıt ol → Login → Sipariş yükle → OCR çalışıyor mu? → Risk uyarısı göster
2. **Risk Alarm Testi**:
   - 3 farklı öğrenci aynı restorandan şikayet et → Restoran RED_FLAG olsun → Yeni sipariş engellensin
3. **Admin Journey**:
   - Dashboard aç → İstatistikleri gör → Riskli restoran manuel ekle → Bildirim gitsin
4. **Load Test**:
   - 100 concurrent kullanıcı → Sipariş yüklesin → OCR tıkanmasın

#### Tools:
- **Unit Tests**: pytest (backend), flutter_test (mobile)
- **Integration Tests**: Postman/Newman (API)
- **Load Testing**: Locust (Python)
- **Security**: OWASP ZAP

---

### Faz 5: Pilot Deployment (0.5 hafta)
**7 Mart - 10 Mart 2026**

#### Hedefler:
- ✅ Isparta Erkek Yurdu'nda pilot uygulama
- ✅ 50-100 öğrenci ile beta test
- ✅ Feedback toplama

#### Setup:
- [ ] Production sunucu kurulumu (DigitalOcean/AWS)
- [ ] Domain: api.gidanobeti.gov.tr
- [ ] SSL sertifikası (Let's Encrypt)
- [ ] Mobile app: TestFlight (iOS) + Internal Testing (Android)
- [ ] Monitoring: Sentry (error tracking)

---

### Faz 6: Feedback & Refinement (1 hafta)
**11 Mart - 17 Mart 2026**

#### Hedefler:
- ✅ Beta kullanıcı feedback'lerini toplama
- ✅ Kritik bug'ları düzeltme
- ✅ UX/UI iyileştirmeleri

#### Focus Areas:
- OCR accuracy (fiş tanıma oranı)
- Uygulama hızı (öğrenciler sabırsız)
- Bildirim sistemi (push notification timing)

---

### Faz 7: Public Release (81 İl) (2-3 ay)
**Mart - Haziran 2026**

#### Rollout Planı (Aşamalı):
1. **Hafta 1-2**: Isparta (2.000 öğrenci)
2. **Hafta 3-4**: 5 pilot şehir (10.000 öğrenci)
3. **Ay 2**: 20 büyük şehir (100.000 öğrenci)
4. **Ay 3**: 81 il (850.000 öğrenci)

---

## 2. SPRINT PLANLAMASI

### Sprint Yapısı
- **Sprint Süresi**: 1 hafta (7 gün)
- **Sprint Review**: Her Cuma 16:00
- **Sprint Planning**: Her Pazartesi 10:00
- **Daily Standup**: Her gün 09:30 (15 dk)

### Sprint 1 (21-27 Ocak) - "Foundation"
**Goal**: Backend + DB + OCR temellerini atmak

| Task ID | Görev | Sahibi | Süre | Durum |
|---------|-------|--------|------|-------|
| S1-1 | Docker Compose setup | Emre | 1g | ⏳ Pending |
| S1-2 | PostgreSQL + Alembic migration | Emre | 1g | ⏳ Pending |
| S1-3 | FastAPI scaffold + models | Emre | 2g | ⏳ Pending |
| S1-4 | EasyOCR test (Türkçe fiş) | Mehmet | 2g | ⏳ Pending |
| S1-5 | Auth endpoints (login/register) | Emre | 2g | ⏳ Pending |

**Definition of Done**:
- [ ] `docker-compose up` çalışıyor
- [ ] Database migrations hatasız
- [ ] POST /auth/login JWT token dönüyor
- [ ] OCR bir fiş fotoğrafını okuyabiliyor

---

### Sprint 2 (28 Ocak - 3 Şubat) - "Core Logic"
**Goal**: Sipariş yükleme endpoint'ini tamamlamak (OCR + DB)

| Task ID | Görev | Sahibi | Süre | Durum |
|---------|-------|--------|------|-------|
| S2-1 | Order upload endpoint (multipart) | Emre | 1g | ⏳ Pending |
| S2-2 | OCR integration (RAM-only processing) | Mehmet | 2g | ⏳ Pending |
| S2-3 | Restaurant name normalization | Emre | 1g | ⏳ Pending |
| S2-4 | Order history endpoint | Emre | 1g | ⏳ Pending |
| S2-5 | Unit tests (pytest) | Mehmet | 2g | ⏳ Pending |

**Definition of Done**:
- [ ] POST /orders/upload görsel alıp OCR yapıyor
- [ ] Görsel sunucuya kaydedilmiyor (RAM only)
- [ ] Restaurant bulunamazsa otomatik oluşturuluyor
- [ ] Test coverage %70+

---

### Sprint 3 (4-10 Şubat) - "Mobile Foundation"
**Goal**: Flutter projesini kurmak ve login ekranını bitirmek

| Task ID | Görev | Sahibi | Süre | Durum |
|---------|-------|--------|------|-------|
| S3-1 | Flutter project init + folder structure | Mehmet | 0.5g | ⏳ Pending |
| S3-2 | Bloc setup + auth bloc | Mehmet | 1g | ⏳ Pending |
| S3-3 | Login/Register UI | Mehmet | 2g | ⏳ Pending |
| S3-4 | API client (Dio + Retrofit) | Mehmet | 1g | ⏳ Pending |
| S3-5 | Secure storage (JWT token) | Mehmet | 0.5g | ⏳ Pending |
| S3-6 | API entegrasyon (login test) | Mehmet | 1g | ⏳ Pending |

**Definition of Done**:
- [ ] Login ekranı çalışıyor (backend'e bağlanıyor)
- [ ] JWT token secure storage'a kaydediliyor
- [ ] Hatalı login'de error mesajı gösteriliyor

---

### Sprint 4 (11-17 Şubat) - "Mobile Core Features"
**Goal**: Ana sayfa + Sipariş yükleme ekranı

| Task ID | Görev | Sahibi | Süre | Durum |
|---------|-------|--------|------|-------|
| S4-1 | Home screen UI (risk panosu) | Mehmet | 2g | ⏳ Pending |
| S4-2 | GET /restaurants/risky endpoint | Emre | 1g | ⏳ Pending |
| S4-3 | Order upload screen (kamera) | Mehmet | 2g | ⏳ Pending |
| S4-4 | Image picker integration | Mehmet | 1g | ⏳ Pending |
| S4-5 | Upload progress indicator | Mehmet | 0.5g | ⏳ Pending |
| S4-6 | Risk warning dialog | Mehmet | 0.5g | ⏳ Pending |

**Definition of Done**:
- [ ] Ana sayfada riskli restoranlar listeleniyor
- [ ] Öğrenci fotoğraf çekip yükleyebiliyor
- [ ] Riskli restoran varsa uyarı gösteriliyor

---

### Sprint 5 (18-24 Şubat) - "Admin Panel"
**Goal**: Web admin dashboard (Next.js)

| Task ID | Görev | Sahibi | Süre | Durum |
|---------|-------|--------|------|-------|
| S5-1 | Next.js project setup | Emre | 0.5g | ⏳ Pending |
| S5-2 | Dashboard API endpoints | Emre | 1g | ⏳ Pending |
| S5-3 | Dashboard UI (Chart.js) | Emre | 2g | ⏳ Pending |
| S5-4 | Restaurant management page | Emre | 2g | ⏳ Pending |
| S5-5 | Order search & filter | Emre | 1g | ⏳ Pending |

**Definition of Done**:
- [ ] Yurt müdürü login yapabiliyor
- [ ] Dashboard istatistikleri gösteriliyor
- [ ] Restoran risk statüsü güncellenebiliyor

---

### Sprint 6 (25 Şubat - 3 Mart) - "Integration & Testing"
**Goal**: End-to-end test ve performance

| Task ID | Görev | Sahibi | Süre | Durum |
|---------|-------|--------|------|-------|
| S6-1 | E2E test senaryoları | Mehmet | 2g | ⏳ Pending |
| S6-2 | Load testing (Locust) | Emre | 1g | ⏳ Pending |
| S6-3 | Security audit (OWASP ZAP) | Emre | 1g | ⏳ Pending |
| S6-4 | Bug fixes | Both | 2g | ⏳ Pending |
| S6-5 | Documentation update | Both | 1g | ⏳ Pending |

**Definition of Done**:
- [ ] Tüm kritik akışlar test edildi
- [ ] Performance target'ları karşılanıyor
- [ ] Bilinen critical bug yok

---

### Sprint 7 (4-10 Mart) - "Pilot Deployment"
**Goal**: Production'a çıkmak

| Task ID | Görev | Sahibi | Süre | Durum |
|---------|-------|--------|------|-------|
| S7-1 | Production sunucu kurulumu | Emre | 1g | ⏳ Pending |
| S7-2 | Domain + SSL setup | Emre | 0.5g | ⏳ Pending |
| S7-3 | Mobile app build (APK + IPA) | Mehmet | 1g | ⏳ Pending |
| S7-4 | Monitoring setup (Sentry) | Emre | 0.5g | ⏳ Pending |
| S7-5 | User onboarding (50 öğrenci) | Both | 2g | ⏳ Pending |

**Definition of Done**:
- [ ] Uygulama production'da çalışıyor
- [ ] 50 öğrenci kayıt olmuş
- [ ] En az 10 sipariş test edilmiş

---

## 3. MILESTONE'LAR

### 🎯 Milestone 1: Backend Ready (3 Şubat 2026)
**Kriterler:**
- [x] FastAPI çalışıyor
- [x] Auth + Order endpoints hazır
- [x] OCR çalışıyor (minimum %80 accuracy)
- [x] Unit test coverage %70+

**Deliverable**: Postman collection ile test edilebilir API

---

### 🎯 Milestone 2: Mobile MVP (17 Şubat 2026)
**Kriterler:**
- [x] Login/Register çalışıyor
- [x] Ana sayfa risk gösteriyor
- [x] Sipariş yükleme çalışıyor
- [x] Backend ile entegre

**Deliverable**: Çalışan APK (internal test)

---

### 🎯 Milestone 3: Admin Dashboard (24 Şubat 2026)
**Kriterler:**
- [x] Yurt müdürü login yapabiliyor
- [x] Dashboard istatistikleri gösteriliyor
- [x] Restoran risk yönetimi çalışıyor

**Deliverable**: Web panel (staging URL)

---

### 🎯 Milestone 4: Pilot Ready (10 Mart 2026)
**Kriterler:**
- [x] Production'da deploy edildi
- [x] 50+ öğrenci aktif kullanıyor
- [x] OCR accuracy %85+
- [x] Kritik bug yok

**Deliverable**: Public beta (TestFlight + Play Store Internal)

---

### 🎯 Milestone 5: Full Rollout (1 Haziran 2026)
**Kriterler:**
- [x] 81 ilde aktif
- [x] 100.000+ kullanıcı
- [x] %99.5 uptime
- [x] Pozitif kullanıcı feedback'leri

**Deliverable**: Public release (App Store + Play Store)

---

## 4. RİSK YÖNETİMİ

### Yüksek Risk Faktörleri

#### 🔴 Risk 1: OCR Accuracy Düşük Olabilir
**Olasılık:** %60  
**Etki:** Kritik (Proje temel fonksiyonu)

**Mitigation:**
- Hybrid OCR (EasyOCR + PaddleOCR fallback)
- Manual entry seçeneği (OCR başarısız olursa)
- Türkçe fiş örnekleriyle yoğun test

**Contingency Plan:**
- Eğer %70'in altındaysa → Manuel giriş zorunlu hale gelir
- 1 ay daha OCR geliştirme

---

#### 🟡 Risk 2: Öğrenci Adoption Düşük
**Olasılık:** %40  
**Etki:** Orta (Kullanıcı sayısı az kalır)

**Mitigation:**
- UX'i mükemmel yap (3 saniyede sipariş kaydet)
- Gamification (puan sistemi - gelecek versiyonda)
- Yurt müdürleri zorunlu hale getirsin

**Contingency Plan:**
- Öğrenci temsilcileriyle tanıtım toplantısı
- İlk 1 haftada yoğun support

---

#### 🟡 Risk 3: Backend Scalability Sorunu
**Olasılık:** %30  
**Etki:** Orta (Yavaşlama, crash)

**Mitigation:**
- Horizontal scaling (Docker Swarm)
- Redis caching (tekrar eden sorgular)
- Load testing ile önceden tespit

**Contingency Plan:**
- CDN kullan (statik dosyalar için)
- Database query optimization

---

#### 🟢 Risk 4: KVKK Uyumsuzluk
**Olasılık:** %20  
**Etki:** Kritik (Yasal sorun)

**Mitigation:**
- Görselleri saklamama garantisi
- TCKN şifreleme
- KVKK uzmanı ile review

**Contingency Plan:**
- Veri silme endpoint'i (GDPR right to be forgotten)

---

## 5. KAYNAK DAĞILIMI

### Takım Yapısı

| Rol | Kişi | Sorumluluk | Haftalık Saat |
|-----|------|------------|---------------|
| **Backend Lead** | Emre | API, DB, OCR, DevOps | 40h |
| **Mobile Lead** | Mehmet | Flutter, UI/UX, Testing | 40h |
| **Full-Stack** | Emre | Admin panel (Next.js) | 20h |
| **Tester** | Mehmet | E2E, Load testing | 10h |

**Toplam Effort:** 110 saat/hafta × 8 hafta = **880 saat**

---

### Technology Budget

| Kategori | Maliyet (Pilot - 3 ay) |
|----------|------------------------|
| **Sunucu (DigitalOcean)** | $50/ay × 3 = $150 |
| **Domain + SSL** | $20/yıl |
| **Firebase (Push Notification)** | Free tier |
| **Sentry (Error Tracking)** | Free tier |
| **Play Store Fee** | $25 (one-time) |
| **App Store Fee** | $99/yıl |
| **Toplam** | ~$300 |

**Production (850K kullanıcı):**
- Sunucu: ~$2.000/ay
- CDN (Cloudflare): $200/ay
- Database backup: $100/ay
- **Yıllık:** ~$27.000

---

## 6. TEST STRATEJİSİ

### Test Pyramid

```
        /\
       /  \  E2E Tests (10%)
      /____\
     /      \  Integration Tests (30%)
    /________\
   /          \  Unit Tests (60%)
  /__________\
```

### Test Coverage Hedefleri

| Katman | Hedef Coverage | Araç |
|--------|----------------|------|
| **Backend** | %80 | pytest + coverage.py |
| **Mobile** | %70 | flutter_test |
| **Admin** | %60 | Jest + React Testing Library |

---

### Test Senaryoları (E2E)

#### Senaryo 1: Başarılı Sipariş Yükleme (Happy Path)
```gherkin
Feature: Sipariş Yükleme
  
  Scenario: Öğrenci güvenli bir restorandan sipariş yükler
    Given Kullanıcı login olmuş
    When Kullanıcı fiş fotoğrafı yükler
    And OCR başarıyla çalışır
    And Restoran risk durumu "SAFE"
    Then Sipariş sisteme kaydedilir
    And Başarı mesajı gösterilir
    And Ana sayfada görünür
```

#### Senaryo 2: Riskli Restoran Uyarısı
```gherkin
Feature: Risk Uyarısı
  
  Scenario: Öğrenci riskli bir restorandan sipariş yükler
    Given Kullanıcı login olmuş
    When Kullanıcı fiş fotoğrafı yükler
    And OCR "X Dönerci" olarak tanır
    And Restoran risk durumu "RED_FLAG"
    Then Kırmızı uyarı pop-up gösterilir
    And "Bu restorandan sipariş vermeyiniz" mesajı çıkar
    And İade destek kartı görünür
```

#### Senaryo 3: OCR Başarısız
```gherkin
Feature: OCR Fallback
  
  Scenario: OCR düşük güven skoru döndürür
    Given Kullanıcı login olmuş
    When Kullanıcı bulanık fiş fotoğrafı yükler
    And OCR confidence < %70
    Then Manuel giriş formu gösterilir
    And Kullanıcı restoran ismini elle girer
    And Sipariş yine de kaydedilir
```

---

### Performance Test Cases

```python
# Locust load test
from locust import HttpUser, task, between

class GidaNobetiUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def view_home(self):
        """Ana sayfayı görüntüle (en sık)"""
        self.client.get(
            "/v1/restaurants/risky",
            headers={"Authorization": f"Bearer {self.token}"}
        )
    
    @task(1)
    def upload_order(self):
        """Sipariş yükle (nadir ama ağır işlem)"""
        with open("test_receipt.jpg", "rb") as f:
            self.client.post(
                "/v1/orders/upload",
                files={"image": f},
                headers={"Authorization": f"Bearer {self.token}"}
            )

# Test target: 500 kullanıcı, 5 dakika
# Expected: %95 success rate, <5s avg response time
```

---

## 7. DEPLOYMENT STRATEJİSİ

### CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run backend tests
        run: |
          cd backend
          pip install -r requirements.txt
          pytest --cov=app tests/
      
      - name: Run mobile tests
        run: |
          cd mobile
          flutter test

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Build Docker image
        run: docker build -t gidanobeti/backend:latest .
      
      - name: Push to registry
        run: docker push gidanobeti/backend:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_IP }}
          username: deploy
          key: ${{ secrets.SSH_KEY }}
          script: |
            docker pull gidanobeti/backend:latest
            docker-compose up -d --no-deps backend
```

---

### Rollback Strategy

**Eğer production'da kritik bug çıkarsa:**
1. Hemen önceki versiyona dön (Docker image tag)
2. Database migration rollback (Alembic)
3. Incident raporu yaz
4. Hotfix branch aç
5. Acil deploy (fast-track CI/CD)

```bash
# Rollback komutu
docker service update --rollback gidanobeti_backend
alembic downgrade -1
```

---

### Monitoring & Alerts

#### Sentry (Error Tracking)
```python
import sentry_sdk

sentry_sdk.init(
    dsn="https://xxx@sentry.io/xxx",
    traces_sample_rate=0.1,  # %10 transaction sample
    profiles_sample_rate=0.1,
)
```

#### Alert Rules (PagerDuty/Email)
- ❌ API error rate > %5 → Instant alert
- ⚠️ OCR queue > 100 backlog → Warning
- ⚠️ Database CPU > %80 → Warning
- ❌ Server down → Instant alert + SMS

---

### Blue-Green Deployment (Gelecek)

```
   [Load Balancer]
         │
    ┌────┴────┐
    │         │
  [Blue]   [Green]
 (Current) (New)

1. Green'e deploy et
2. Test et (health check)
3. Traffic'i yavaşça Green'e kaydır
4. Blue'yu kapat
```

---

## 8. BAŞARI KRİTERLERİ (KPI)

### Teknik KPI'lar

| Metrik | Hedef (Pilot) | Hedef (Production) |
|--------|---------------|-------------------|
| **OCR Accuracy** | %80+ | %90+ |
| **API Uptime** | %99.0 | %99.5 |
| **Upload Success Rate** | %95+ | %98+ |
| **Avg Upload Time** | <5s | <3s |
| **Daily Active Users** | 30% (15/50) | 20% (170K/850K) |
| **Orders per Day** | 20+ | 300K+ |

### İş KPI'ları

| Metrik | Hedef |
|--------|-------|
| **Kullanıcı Memnuniyeti** | 4.0+/5.0 (App Store rating) |
| **Risk Detection Accuracy** | 100% (hiçbir riskli restoran kaçmasın) |
| **Vaka Çözüm Süresi** | <2 saat (kaynak tespiti) |
| **Yurt Benimseme Oranı** | %80 (64/81 il) |

---

## 9. İLETİŞİM PLANI

### Haftalık Ritim

- **Pazartesi 10:00**: Sprint planning (1 saat)
- **Her gün 09:30**: Daily standup (15 dk)
- **Cuma 16:00**: Sprint review + retro (1 saat)

### Haftalık Rapor (Her Cuma)

```markdown
## Haftalık Rapor - [Tarih]

### ✅ Tamamlanan
- [ ] Task 1
- [ ] Task 2

### 🚧 Devam Eden
- [ ] Task 3 (50% tamamlandı)

### ❌ Blocker
- Issue X (bekliyor: API key approval)

### 📊 Metrikler
- Code coverage: 75%
- Open bugs: 3 (1 critical)
- Sprint velocity: 25 points

### 📅 Gelecek Hafta
- Task 4
- Task 5
```

---

## 10. KAYNAKLAR VE REFERANSLAR

### Dokümantasyon
- [SPEC.md](./SPEC.md) - Teknik detaylar
- [TASKS.md](./TASKS.md) - Detaylı görev listesi
- [API Docs](http://localhost:8000/docs) - Swagger UI

### Araçlar
- **Project Management**: GitHub Projects
- **Design**: Figma
- **API Testing**: Postman
- **Communication**: Slack/Discord

---

## 📌 NOTLAR

### Güncellemeler
- **21 Ocak 2026**: İlk plan oluşturuldu
- _Tüm değişiklikler bu bölüme loglanacak_

### Sorumlu İletişim
- **Emre**: [email/telefon]
- **Mehmet**: [email/telefon]

---

**Plan Onay:**
- [ ] Emre - 21 Ocak 2026
- [ ] Mehmet - 21 Ocak 2026

**Planlanan Başlangıç:** 21 Ocak 2026, Pazartesi 09:00  
**Hedef Bitiş:** 15 Mart 2026, Cuma 18:00

---

_"Mükemmel plan olmaz, ama uyarlanabilir plan olur. Bu plan yaşayan bir dokümandır."_ 🚀
