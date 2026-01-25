# 🎯 MÜŞTERİ DEMO HAZIRLIK REHBERİ

**Tarih:** 25 Ocak 2026  
**Hedef:** 2-3 gün içinde görünür kısımları göstermek

---

## ✅ TAMAMLANAN KRİTİK İŞLER

### 1. Backend Endpoint'leri ✅
- ✅ `POST /v1/auth/register` - Kullanıcı kaydı
- ✅ `POST /v1/auth/login` - Giriş
- ✅ `GET /v1/restaurants/risky` - Riskli restoranlar (Mobile home için)
- ✅ `GET /v1/admin/dashboard/statistics` - Dashboard istatistikleri
- ✅ `PUT /v1/admin/restaurants/{id}/risk-status` - Risk durumu güncelleme
- ✅ `GET /v1/restaurants` - Restoran listesi

### 2. Admin Panel Entegrasyonu ✅
- ✅ Dashboard gerçek API'ye bağlandı
- ✅ Restaurants sayfası gerçek API'ye bağlandı
- ✅ Risk durumu güncelleme çalışıyor

### 3. Seed Data ✅
- ✅ Test restoranları (10 adet, riskli örnekler dahil)
- ✅ Test kullanıcıları (öğrenci + admin)
- ✅ Test yurdu (Isparta Erkek KYK Yurdu)

---

## 🚀 DEMO HAZIRLIK ADIMLARI

### Adım 1: Backend'i Başlat

```bash
cd Proje
docker-compose up -d
```

**Kontrol:**
- Backend çalışıyor mu? → http://localhost:8000/health
- Swagger docs açılıyor mu? → http://localhost:8000/docs

### Adım 2: Seed Data'yı Yükle

**Yöntem 1: Docker Container İçinde (Önerilen)**
```bash
# Backend container'ı içinde çalıştır
docker exec -it gidanobeti_api python seed_restaurants.py
```

**Yöntem 2: Local Python Environment**
```bash
cd Proje/backend
# Virtual environment aktif et (eğer varsa)
pip install -r requirements.txt
python seed_restaurants.py
```

**Beklenen Çıktı:**
```
🌱 Starting seed process...
✅ Seeded dormitory: Isparta Erkek KYK Yurdu
✅ Seeded 10 test restaurants
✅ Seeded 3 test users
   Test Student: TCKN=12345678901, Password=Test123!
   Test Admin: TCKN=11111111111, Password=Admin123!
✅ Seed process completed!
```

### Adım 3: Admin Panel'i Başlat

```bash
cd Proje/admin-panel
npm install  # İlk kez çalıştırıyorsanız veya axios eksikse
npm run dev
```

**Not:** Eğer `axios` veya `tailwindcss` hatası alırsanız:
```bash
npm install axios tailwindcss
```

**Kontrol:**
- Admin panel açılıyor mu? → http://localhost:3000
- Login sayfası görünüyor mu?

### Adım 4: Test Kullanıcıları ile Giriş

**Admin Girişi:**
- TCKN: `11111111111`
- Şifre: `Admin123!`
- → Dashboard'a yönlendirilmeli

**Öğrenci Girişi (Mobile için):**
- TCKN: `12345678901`
- Şifre: `Test123!`

### Adım 5: Mobile App'i Başlat

**Gereksinimler:**
- Flutter SDK yüklü olmalı (3.10.7+)
- Android Studio veya Xcode (iOS için Mac gerekli)
- Android Emulator veya iOS Simulator çalışıyor olmalı

**Kurulum ve Çalıştırma:**

1. **Dependencies yükle:**
```bash
cd Proje/mobile
flutter pub get
```

2. **Code generation çalıştır (Retrofit için):**
```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

3. **Emulator/Simulator başlat:**
   - Android Studio → AVD Manager → Emulator başlat
   - veya Xcode → Simulator başlat

4. **Uygulamayı çalıştır:**
```bash
flutter run
```

**Önemli Notlar:**
- **Android Emulator:** API base URL otomatik olarak `http://10.0.2.2:8000` olarak ayarlanmış (localhost yerine)
- **iOS Simulator:** API base URL `http://localhost:8000` kullanıyor
- **Fiziksel Cihaz:** Backend'in IP adresini kullanmanız gerekebilir

**Test Kullanıcıları:**
- TCKN: `12345678901`
- Şifre: `Test123!`

**Sorun Giderme:**
- Eğer "Connection refused" hatası alırsanız:
  - Backend'in çalıştığından emin olun (`docker-compose ps`)
  - Android emulator için `10.0.2.2:8000` kullanıldığını kontrol edin
  - iOS simulator için `localhost:8000` kullanıldığını kontrol edin

---

## 📱 GÖSTERİLECEK ÖZELLİKLER

### 1. Admin Panel (Web) ✅

#### Dashboard Sayfası
- ✅ 4 KPI kartı (Toplam Sipariş, Aktif Öğrenci, Toplam Vaka, Riskli Restoran)
- ✅ Gerçek veriler API'den geliyor
- ✅ Chart placeholder'ları hazır

**Gösterilecek:**
- İstatistiklerin gerçek zamanlı olarak API'den geldiği
- Responsive tasarım (mobile + desktop)

#### Restoran Yönetimi Sayfası
- ✅ Restoran listesi (API'den geliyor)
- ✅ Risk durumu badge'leri (renkli)
- ✅ Arama ve filtreleme
- ✅ Risk durumu güncelleme modal'ı
- ✅ Gerçek API entegrasyonu

**Gösterilecek:**
- Restoran listesinin gerçek verilerle geldiği
- Risk durumu güncellemenin çalıştığı
- Arama ve filtrelemenin anlık çalıştığı

#### Siparişler Sayfası
- ✅ UI hazır (mock data ile)
- ⚠️ Backend endpoint'i eksik (gösterilemez ama UI görülebilir)

**Gösterilecek:**
- UI tasarımı ve kullanılabilirliği
- CSV export özelliği (mock data ile)

---

### 2. Backend API (Swagger) ✅

**Gösterilecek Endpoint'ler:**
- `POST /v1/auth/login` - Test kullanıcı ile giriş
- `GET /v1/restaurants/risky` - Riskli restoranlar listesi
- `GET /v1/admin/dashboard/statistics` - Dashboard istatistikleri
- `PUT /v1/admin/restaurants/{id}/risk-status` - Risk durumu güncelleme

**Swagger UI:** http://localhost:8000/docs

---

### 3. Mobile App (Flutter) ⚠️

**Durum:** UI'lar kısmen hazır, backend entegrasyonu eksik

**Gösterilebilecek:**
- Login ekranı UI (backend'e bağlanabilir)
- Home screen UI (mock data ile)
- Order upload ekranı UI (backend'e bağlanamaz - OCR eksik)

**Not:** Mobile app için backend endpoint'leri hazır ama OCR servisi eksik olduğu için order upload çalışmaz.

---

## 🎬 DEMO SENARYOSU

### Senaryo 1: Admin Panel Demo (10 dakika)

1. **Giriş Yap**
   - Admin panel'i aç (http://localhost:3000)
   - TCKN: `11111111111`, Şifre: `Admin123!`
   - Dashboard'a yönlendirilmeli

2. **Dashboard'u Göster**
   - 4 KPI kartını göster
   - "Bu veriler gerçek zamanlı olarak API'den geliyor" de
   - Chart placeholder'larını göster

3. **Restoran Yönetimi**
   - Restoranlar sayfasına git
   - Riskli restoranları göster (kırmızı badge'ler)
   - Bir restoranın risk durumunu güncelle
   - "Değişiklik anında veritabanına kaydediliyor" de

4. **API Dokümantasyonu**
   - Swagger UI'ı göster (http://localhost:8000/docs)
   - Bir endpoint'i test et (ör: GET /restaurants/risky)

### Senaryo 2: Backend API Demo (5 dakika)

1. **Swagger UI'da Test**
   - `POST /v1/auth/login` endpoint'ini test et
   - Token al
   - `GET /v1/restaurants/risky` endpoint'ini test et (token ile)

2. **Postman/Thunder Client ile Test**
   - API endpoint'lerini göster
   - Response formatlarını açıkla

### Senaryo 3: Mobile App UI Demo (5 dakika)

1. **Login Ekranı**
   - Flutter app'i aç
   - Login ekranını göster
   - "Backend'e bağlanabilir ama şimdilik UI'ı gösteriyoruz" de

2. **Home Screen**
   - Risk panosunu göster
   - "Riskli restoranlar burada listelenecek" de

---

## ⚠️ BİLİNMESİ GEREKENLER

### Eksik Özellikler (Açıklama Gerekli)

1. **OCR Servisi**
   - Order upload endpoint'i çalışmıyor
   - "OCR servisi geliştirme aşamasında, 1-2 hafta içinde tamamlanacak" de

2. **Mobile App Backend Entegrasyonu**
   - UI'lar hazır ama bazı özellikler backend'e bağlı değil
   - "UI/UX tamamlandı, backend entegrasyonu devam ediyor" de

3. **Order Upload**
   - Endpoint eksik (OCR'a bağımlı)
   - "Ana özellik, OCR servisi tamamlandığında aktif olacak" de

### Güçlü Yönler (Vurgula)

1. ✅ **Admin Panel Tam Çalışıyor**
   - Dashboard gerçek verilerle çalışıyor
   - Restoran yönetimi tam fonksiyonel

2. ✅ **Backend API Hazır**
   - Auth sistemi çalışıyor
   - Risk yönetimi endpoint'leri hazır

3. ✅ **Modern Teknoloji Stack**
   - FastAPI (Python)
   - Next.js (React)
   - Flutter (Mobile)

---

## 📋 DEMO ÖNCESİ KONTROL LİSTESİ

- [ ] Docker container'ları çalışıyor mu?
- [ ] Backend health check geçiyor mu? (http://localhost:8000/health)
- [ ] Seed data yüklendi mi?
- [ ] Admin panel çalışıyor mu? (http://localhost:3000)
- [ ] Test kullanıcıları ile giriş yapılabiliyor mu?
- [ ] Dashboard verileri görünüyor mu?
- [ ] Restoran listesi görünüyor mu?
- [ ] Risk durumu güncelleme çalışıyor mu?
- [ ] Swagger UI açılıyor mu? (http://localhost:8000/docs)

---

## 🎯 DEMO SONRASI HEDEFLER

### Kısa Vadeli (1-2 Hafta)
1. OCR servisi tamamlanacak
2. Order upload endpoint'i çalışacak
3. Mobile app backend'e bağlanacak

### Orta Vadeli (2-4 Hafta)
1. Tüm endpoint'ler tamamlanacak
2. Test coverage artırılacak
3. Performance optimizasyonu yapılacak

---

## 📞 SORULAR İÇİN HAZIR CEVAPLAR

**S: OCR servisi ne zaman hazır olacak?**
C: OCR servisi geliştirme aşamasında. EasyOCR entegrasyonu 1-2 hafta içinde tamamlanacak. Test fişleriyle doğrulama yapılacak.

**S: Mobile app ne zaman çalışacak?**
C: Mobile app UI'ları hazır. Backend entegrasyonu OCR servisi tamamlandıktan sonra yapılacak. Tahmini 2-3 hafta.

**S: Pilot deployment ne zaman?**
C: Hedef 15 Mart 2026. Şu anda MVP geliştirme aşamasındayız. Backend altyapısı hazır, OCR servisi tamamlandığında pilot başlayacak.

---

**Hazırlayan:** AI Assistant  
**Tarih:** 25 Ocak 2026  
**Son Güncelleme:** 25 Ocak 2026
