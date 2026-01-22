# 🍽️ Gıda Nöbeti - Kurulum ve Çalıştırma Rehberi

## 📋 İçindekiler
- [Hızlı Başlangıç](#hızlı-başlangıç-tek-komut)
- [Manuel Kurulum](#manuel-kurulum)
- [Sistem Gereksinimleri](#sistem-gereksinimleri)
- [Proje Yapısı](#proje-yapısı)
- [Sorun Giderme](#sorun-giderme)

---

## 🚀 Hızlı Başlangıç (TEK KOMUT)

### Tüm Uygulamaları Başlat
```cmd
START.bat
```
veya PowerShell'de:
```powershell
powershell -ExecutionPolicy Bypass -File "C:\Users\emrem\Desktop\GidaNobeti\Proje\START.ps1"
```

Bu komut otomatik olarak şunları yapar:
1. ✅ Docker servisleri başlatır (PostgreSQL + Redis)
2. ✅ Backend API başlatır (FastAPI - Port 8000)
3. ✅ Admin Panel başlatır (Next.js - Port 3000)
4. ✅ Mobile App başlatır (Flutter - Cihaz seçimi yaparsınız)

### Tüm Uygulamaları Durdur
```cmd
STOP.bat
```
veya PowerShell'de:
```powershell
powershell -ExecutionPolicy Bypass -File "C:\Users\emrem\Desktop\GidaNobeti\Proje\STOP.ps1"
```

---

## 📦 Sistem Gereksinimleri

### Zorunlu
- ✅ **Windows 11** (veya Windows 10 21H2+)
- ✅ **Docker Desktop** 4.0+ (PostgreSQL + Redis için)
- ✅ **Node.js** 18.17+ (Admin Panel için)
- ✅ **Python** 3.11+ (Backend için)
- ✅ **Flutter** 3.38.7+ (Mobile App için)
- ✅ **Git** 2.40+

### Opsiyonel
- Android Studio (Android emulator için)
- Visual Studio Code (geliştirme için)
- Postman (API test için)

---

## 🏗️ Proje Yapısı

```
GidaNobeti/Proje/
├── 📦 backend/              # FastAPI Backend (Python)
│   ├── app/
│   │   ├── main.py         # FastAPI uygulaması
│   │   ├── api/            # API endpoints
│   │   ├── models/         # SQLAlchemy modelleri
│   │   ├── schemas/        # Pydantic schemas
│   │   └── core/           # Config, security
│   ├── alembic/            # Database migrations
│   ├── requirements.txt    # Python dependencies
│   └── .env                # Environment variables
│
├── ⚛️  admin-panel/         # Next.js Admin Panel (React + TypeScript)
│   ├── app/                # Next.js 16 App Router
│   │   ├── dashboard/      # Admin sayfaları
│   │   └── login/          # Giriş sayfası
│   ├── components/         # React bileşenleri
│   ├── lib/                # Utilities
│   └── package.json        # Node dependencies
│
├── 📱 mobile/               # Flutter Mobile App (Android + iOS)
│   ├── lib/
│   │   ├── core/           # Core utilities
│   │   │   ├── constants/  # App sabitleri
│   │   │   └── bloc/       # BLoC altyapısı
│   │   ├── features/       # Özellikler (auth, home, etc)
│   │   └── main.dart       # Ana dosya
│   └── pubspec.yaml        # Flutter dependencies
│
├── 📄 docs/                 # Dokümantasyon
│   ├── TASKS.md            # Görev listesi
│   └── SPEC.md             # Teknik özellikler
│
├── 🐳 docker-compose.yml    # Docker servisleri
├── 🚀 START.ps1             # TEK KOMUT BAŞLATMA
└── 🛑 STOP.ps1              # TEK KOMUT DURDURMA
```

---

## 🔧 Manuel Kurulum (İlk Kez)

### 1. Repository'yi Klonla
```powershell
git clone <repository-url>
cd GidaNobeti/Proje
```

### 2. Docker Servisleri Başlat
```powershell
docker-compose up -d
```
- PostgreSQL: `localhost:5432` (User: `gidanobeti`, Pass: `secure_password_here`)
- Redis: `localhost:6379`

### 3. Backend Kurulum (FastAPI)
```powershell
cd backend

# Virtual environment oluştur (ilk kez)
python -m venv ..\.venv

# Aktif et
& ..\.venv\Scripts\Activate.ps1

# Dependencies yükle
pip install -r requirements.txt

# Database migrate (ilk kez)
alembic upgrade head

# Başlat
uvicorn app.main:app --reload
```
**Erişim:** http://localhost:8000  
**API Docs:** http://localhost:8000/docs

### 4. Admin Panel Kurulum (Next.js)
```powershell
cd admin-panel

# Dependencies yükle (ilk kez)
npm install

# Başlat
npm run dev
```
**Erişim:** http://localhost:3000

### 5. Mobile App Kurulum (Flutter)
```powershell
cd mobile

# Dependencies yükle (ilk kez)
flutter pub get

# Cihazları kontrol et
flutter devices

# Başlat
flutter run
```
**Cihaz Seçenekleri:**
- Edge (web) - Tarayıcıda açılır
- Android Emulator - Android simülasyonu
- Windows Desktop - Masaüstü uygulaması (Developer Mode gerekir)

---

## 📍 Erişim Adresleri

| Servis | URL | Açıklama |
|--------|-----|----------|
| 🐘 PostgreSQL | `localhost:5432` | Veritabanı (User: gidanobeti) |
| 🔴 Redis | `localhost:6379` | Cache & Queue |
| 🐍 Backend API | http://localhost:8000 | FastAPI REST API |
| 📚 API Docs | http://localhost:8000/docs | Swagger UI |
| ⚛️ Admin Panel | http://localhost:3000 | Next.js Admin |
| 📱 Mobile App | (Cihaza göre) | Flutter App |

---

## ⚙️ Geliştirme Komutları

### Backend
```powershell
cd backend

# Server başlat (hot reload)
uvicorn app.main:app --reload

# Database migration oluştur
alembic revision --autogenerate -m "mesaj"

# Migration uygula
alembic upgrade head

# Test çalıştır
pytest

# Linting
ruff check app/
```

### Admin Panel
```powershell
cd admin-panel

# Dev server (hot reload)
npm run dev

# Production build
npm run build

# Production başlat
npm start

# Type check
npx tsc --noEmit

# Linting
npm run lint
```

### Mobile
```powershell
cd mobile

# Dev mode (hot reload)
flutter run

# Code generation (BLoC, Retrofit)
flutter pub run build_runner build --delete-conflicting-outputs

# Test
flutter test

# Build APK
flutter build apk --release

# Build iOS (macOS'ta)
flutter build ios --release

# Analyze
flutter analyze
```

---

## 🔍 Sorun Giderme

### ❌ Docker servisleri başlamıyor
**Çözüm:**
1. Docker Desktop açık mı kontrol edin
2. `docker-compose down` → `docker-compose up -d`
3. Port çakışması varsa: `docker ps` ile kontrol edin

### ❌ Backend başlamıyor
**Çözüm:**
1. Virtual environment aktif mi: `& ..\.venv\Scripts\Activate.ps1`
2. Dependencies yüklü mü: `pip install -r requirements.txt`
3. PostgreSQL erişilebilir mi: `docker ps | findstr postgres`
4. `.env` dosyası var mı: `cp .env.example .env`

### ❌ Admin Panel başlamıyor
**Çözüm:**
1. Node.js versiyonu: `node --version` (18.17+)
2. Dependencies yüklü mü: `npm install`
3. Port 3000 boş mu: `netstat -ano | findstr :3000`

### ❌ Mobile App başlamıyor
**Çözüm:**
1. Flutter kurulu mu: `flutter doctor`
2. Dependencies yüklü mü: `flutter pub get`
3. Android emulator çalışıyor mu: `flutter devices`
4. Windows Developer Mode aktif mi (masaüstü için): `start ms-settings:developers`

### ❌ "Cannot find module" hatası (Node.js)
**Çözüm:**
```powershell
cd admin-panel
rm -r node_modules
rm package-lock.json
npm install
```

### ❌ "pubspec.yaml not found" hatası (Flutter)
**Çözüm:**
```powershell
# Doğru dizinde olduğunuzdan emin olun
cd C:\Users\emrem\Desktop\GidaNobeti\Proje\mobile
flutter pub get
```

### ❌ Database migration hatası
**Çözüm:**
```powershell
cd backend
# Son migration'ı geri al
alembic downgrade -1
# Tekrar uygula
alembic upgrade head
```

---

## 🔄 Port Bilgileri

| Servis | Port | Değiştirme |
|--------|------|-----------|
| PostgreSQL | 5432 | `docker-compose.yml` içinde |
| Redis | 6379 | `docker-compose.yml` içinde |
| Backend | 8000 | `uvicorn --port XXXX` |
| Admin Panel | 3000 | `package.json` scripts içinde `-p XXXX` |
| Mobile | - | Cihaza göre değişir |

---

## 📝 Ekstra Notlar

### Hot Reload
- ✅ **Backend:** Code değiştiğinde otomatik reload
- ✅ **Admin Panel:** Code değiştiğinde otomatik reload
- ✅ **Mobile:** `r` tuşuna basarak hot reload, `R` ile hot restart

### Environment Variables
- **Backend:** `backend/.env` dosyasında
- **Admin Panel:** `admin-panel/.env.local` (oluşturulacak)
- **Mobile:** `lib/core/constants/app_constants.dart` içinde

### Database Reset
```powershell
# Tüm data'yı sil ve yeniden başlat
docker-compose down -v
docker-compose up -d
cd backend
alembic upgrade head
```

---

## 🚀 Production Deployment

### Backend (FastAPI)
```powershell
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Admin Panel (Next.js)
```powershell
cd admin-panel
npm run build
npm start
```

### Mobile (Flutter)
```powershell
cd mobile
# Android
flutter build apk --release
# iOS (macOS'ta)
flutter build ios --release
```

---

## 📞 Destek

- **Dokümantasyon:** `docs/SPEC.md` ve `docs/TASKS.md`
- **API Dokümantasyonu:** http://localhost:8000/docs
- **Issues:** GitHub Issues

---

## 📄 Lisans

[Lisans bilgisi buraya]

---

**Hazırlayan:** Emre & Mehmet  
**Son Güncelleme:** 23 Ocak 2026
