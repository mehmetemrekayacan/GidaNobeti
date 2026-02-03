# 🚀 GELİŞTİRME ORTAMI BAŞLATMA REHBERİ

**Hedef:** Her PC açıldığında projeyi çalıştırmak için adım adım rehber  
**Tahmini Süre:** 5-10 dakika

---

## 📋 BAŞLANGIÇ ÖN HAZIRLIK (İlk Kurulum - Sadece Bir Kez)

### 1. Gereksinimler Kontrolü

**Backend için:**
- ✅ Docker Desktop yüklü ve çalışıyor olmalı
- ✅ Docker Compose yüklü olmalı

**Admin Panel için:**
- ✅ Node.js 18+ yüklü olmalı
- ✅ npm veya yarn yüklü olmalı

**Mobile App için:**
- ✅ Flutter SDK 3.10.7+ yüklü olmalı
- ✅ Android Studio veya Xcode (iOS için) yüklü olmalı

**Kontrol Komutları:**
```bash
docker --version
docker-compose --version
node --version
npm --version
flutter --version
```

### 2. İlk Kurulum (Sadece Bir Kez)

```bash
# 1. Proje dizinine git
cd C:\Users\emrem\Desktop\GidaNobeti\Proje

# 2. Admin Panel dependencies yükle (sadece ilk kez)
cd admin-panel
npm install
cd ..

# 3. Mobile App dependencies yükle (sadece ilk kez)
cd mobile
flutter pub get
cd ..
```

---

## 🔄 GÜNLÜK BAŞLATMA ADIMLARI

### Adım 1: Docker Desktop'ı Başlat ⏱️ 1-2 dakika

**Windows'ta:**
1. Docker Desktop uygulamasını açın
2. Docker'ın tamamen başlamasını bekleyin (sistem tray'de yeşil olmalı)
3. Terminal'de kontrol edin:
```bash
docker ps
```

**Kontrol:** Docker çalışıyorsa container listesi görünmeli (boş liste de olabilir, sorun değil).

---

### Adım 2: Backend'i Başlat ⏱️ 2-3 dakika

```bash
# Proje dizinine git
cd C:\Users\emrem\Desktop\GidaNobeti\Proje

# Docker container'ları başlat
docker-compose up -d
```

**Beklenen Çıktı:**
```
[+] Running 3/3
 ✔ Container gidanobeti_postgres    Started
 ✔ Container gidanobeti_redis       Started
 ✔ Container gidanobeti_api         Started
```

**Kontrol:**
```bash
# Container'ların çalıştığını kontrol et
docker-compose ps

# Backend health check
curl http://localhost:8000/health
# Veya tarayıcıda: http://localhost:8000/health
```

**Başarılı:** `{"status":"healthy",...}` mesajı görünmeli.

**Sorun Giderme:**
- Eğer container'lar başlamazsa: `docker-compose logs` ile logları kontrol edin
- Port 8000 kullanılıyorsa: `docker-compose down` yapıp tekrar `docker-compose up -d` deneyin

---

### Adım 3: Seed Data Kontrolü/Yükleme ⏱️ 30 saniye

**İlk Kez veya Veritabanı Temizlendiyse:**
```bash
# Seed script'i çalıştır
docker exec -it gidanobeti_api python seed_restaurants.py
```

**Beklenen Çıktı:**
```
🌱 Starting seed process...
✅ Seeded dormitory: Isparta Erkek KYK Yurdu
✅ Seeded 10 test restaurants
✅ Admin user already exists (TCKN: 11111111111)
✅ Student user already exists (TCKN: 12345678901)
✅ Seed process completed!
```

**Not:** Eğer seed data zaten varsa, script "already exists" mesajları verecek. Bu normaldir.

**Kontrol:**
- Swagger UI'da test: http://localhost:8000/docs
- `POST /v1/auth/login` endpoint'ini test edin (TCKN: `11111111111`, Password: `Admin123!`)

---

### Adım 4: Admin Panel'i Başlat ⏱️ 1-2 dakika

**Yeni Terminal Açın (Backend terminal'ini kapatmayın):**

```bash
# Proje dizinine git
cd C:\Users\emrem\Desktop\GidaNobeti\Proje\admin-panel

# Development server'ı başlat
npm run dev
```

**Beklenen Çıktı:**
```
  ▲ Next.js 15.x.x
  - Local:        http://localhost:3000
  - Ready in 2.5s
```

**Kontrol:**
- Tarayıcıda açın: http://localhost:3000
- Login sayfası görünmeli

**Test Girişi:**
- TCKN: `11111111111`
- Şifre: `Admin123!`
- Dashboard'a yönlendirilmeli

**Sorun Giderme:**
- Eğer `npm run dev` hata verirse:
  ```bash
  npm install  # Dependencies'leri tekrar yükle
  npm run dev
  ```

---

### Adım 5: Mobile App'i Başlat (Opsiyonel) ⏱️ 3-5 dakika

**Sadece Mobile App geliştiriyorsanız:**

**5.1. Android Emulator Başlat:**
- Android Studio'yu açın
- Device Manager'dan emulator'ü başlatın (▶️ butonu)
- Veya terminal'den:
```bash
flutter emulators --launch "Medium_Phone_API_36.1"
```

**5.2. Flutter App'i Çalıştır:**

**Yeni Terminal Açın:**

```bash
# Proje dizinine git
cd C:\Users\emrem\Desktop\GidaNobeti\Proje\mobile

# Dependencies kontrolü (ilk kez veya pubspec.yaml değiştiyse)
flutter pub get

# Uygulamayı çalıştır
flutter run
```

**Veya Belirli Emulator'e:**
```bash
flutter run -d emulator-5554
```

**Beklenen Çıktı:**
```
Launching lib\main.dart on sdk gphone64 x86 64 in debug mode...
Running Gradle task 'assembleDebug'...
√ Built build\app\outputs\flutter-apk\app-debug.apk
Installing build\app\outputs\flutter-apk\app-debug.apk...
```

**Kontrol:**
- Emulator'de uygulama açılmalı
- Login ekranı görünmeli

**Test Girişi:**
- TCKN: `12345678901`
- Şifre: `Test123!`

---

## ✅ HIZLI KONTROL LİSTESİ

Her başlatmada şunları kontrol edin:

- [ ] Docker Desktop çalışıyor mu?
- [ ] Backend container'ları çalışıyor mu? (`docker-compose ps`)
- [ ] Backend health check geçiyor mu? (http://localhost:8000/health)
- [ ] Swagger UI açılıyor mu? (http://localhost:8000/docs)
- [ ] Admin Panel açılıyor mu? (http://localhost:3000)
- [ ] Admin login çalışıyor mu? (TCKN: `11111111111`, Şifre: `Admin123!`)
- [ ] (Opsiyonel) Mobile App çalışıyor mu?

---

## 🛑 GELİŞTİRME BİTTİĞİNDE DURDURMA

### Backend'i Durdurma:
```bash
cd C:\Users\emrem\Desktop\GidaNobeti\Proje
docker-compose down
```

**Not:** `docker-compose down` veritabanını silmez, sadece container'ları durdurur.

### Admin Panel'i Durdurma:
- Terminal'de `Ctrl + C` basın

### Mobile App'i Durdurma:
- Terminal'de `q` tuşuna basın veya `Ctrl + C`

---

## 🔧 SIK KARŞILAŞILAN SORUNLAR VE ÇÖZÜMLERİ

### Sorun 1: Port 8000 Zaten Kullanılıyor

**Çözüm:**
```bash
# Hangi process port 8000'i kullanıyor?
netstat -ano | findstr :8000

# Process'i kapat (PID'yi yukarıdaki komuttan alın)
taskkill /PID <PID> /F

# Veya Docker container'ı kapat
docker-compose down
docker-compose up -d
```

### Sorun 2: Docker Container'ları Başlamıyor

**Çözüm:**
```bash
# Logları kontrol et
docker-compose logs

# Container'ları temizle ve yeniden başlat
docker-compose down
docker-compose up -d

# Eğer hala sorun varsa, Docker Desktop'ı yeniden başlatın
```

### Sorun 3: Admin Panel "Cannot connect to API"

**Çözüm:**
1. Backend'in çalıştığını kontrol edin: http://localhost:8000/health
2. Admin Panel'i yeniden başlatın (`Ctrl + C` → `npm run dev`)
3. Tarayıcı cache'ini temizleyin

### Sorun 4: Seed Data Yüklenmiyor

**Çözüm:**
```bash
# Container içine girip manuel çalıştır
docker exec -it gidanobeti_api bash
python seed_restaurants.py
exit
```

### Sorun 5: Mobile App "Connection Refused"

**Çözüm:**
1. Backend'in çalıştığını kontrol edin: http://localhost:8000/health
2. Android Emulator için API URL: `http://10.0.2.2:8000` (localhost yerine)
3. iOS Simulator için API URL: `http://localhost:8000`

---

## 📝 HIZLI BAŞLATMA SCRIPT'İ (Opsiyonel)

Windows için `.bat` dosyası oluşturabilirsiniz:

**`start-dev.bat`** (Proje kök dizininde):
```batch
@echo off
echo Starting development environment...

echo [1/4] Starting Docker containers...
cd Proje
docker-compose up -d

echo [2/4] Waiting for backend to be ready...
timeout /t 10

echo [3/4] Checking backend health...
curl http://localhost:8000/health

echo [4/4] Starting Admin Panel...
start cmd /k "cd Proje\admin-panel && npm run dev"

echo.
echo ✅ Development environment started!
echo.
echo Backend: http://localhost:8000
echo Admin Panel: http://localhost:3000
echo Swagger: http://localhost:8000/docs
echo.
pause
```

**Kullanım:**
```bash
# Çift tıklayarak çalıştırın veya:
start-dev.bat
```

---

## 🎯 ÖZET: GÜNLÜK BAŞLATMA SIRASI

1. **Docker Desktop'ı aç** (1-2 dk)
2. **Backend'i başlat:** `docker-compose up -d` (2-3 dk)
3. **Seed data kontrol:** `docker exec -it gidanobeti_api python seed_restaurants.py` (30 sn)
4. **Admin Panel'i başlat:** `cd admin-panel && npm run dev` (1-2 dk)
5. **Mobile App (opsiyonel):** `cd mobile && flutter run` (3-5 dk)

**Toplam Süre:** ~5-10 dakika

---

## 📞 YARDIM

Sorun yaşarsanız:
1. `DEMO_FIXES.md` dosyasına bakın
2. `docker-compose logs` ile logları kontrol edin
3. Backend health check: http://localhost:8000/health

---

**Son Güncelleme:** 25 Ocak 2026  
**Hazırlayan:** AI Assistant
