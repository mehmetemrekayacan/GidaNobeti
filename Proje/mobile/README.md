# Gıda Nöbeti - Mobile App

Flutter mobil uygulama projesi.

## 🚀 Başlangıç

### Gereksinimler
- Flutter 3.x+ (Dart 3.x+)
- Android Studio (Android emulator için)
- Backend çalışıyor olmalı: `docker-compose up -d` (Proje kökünde)

### Android Studio ile çalıştırma (kısa)

1. **Backend:** `Proje` dizininde `docker-compose up -d`
2. **Emulator:** Android Studio → Device Manager → bir cihaz seçip ▶️ ile başlat
3. **Mobil:**
```bash
cd Proje/mobile
flutter pub get
flutter run
```
Emulator açıksa uygulama orada açılır. Test girişi: TCKN `12345678901`, Şifre `Test123!` (seed verisi gerekir).

**Detaylı adımlar ve sorun giderme:** `Proje/docs/MOBILE_RUN.md`

## 📁 Proje Yapısı

```
lib/
├── core/                    # Core functionality
│   ├── constants/          # App constants
│   ├── theme/              # Theme configuration
│   └── utils/              # Utility functions
├── features/               # Feature modules
│   ├── auth/              # Authentication
│   ├── home/              # Home screen
│   ├── order/             # Order upload
│   └── profile/           # User profile
└── main.dart              # Entry point
```

## 🏗️ Architecture

- **State Management:** BLoC Pattern
- **API Client:** Dio + Retrofit
- **Storage:** flutter_secure_storage
- **Navigation:** go_router

## 📦 Dependencies

Temel dependencies için `pubspec.yaml` dosyasına bakın.

## 🔧 Development

### Code Generation
```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

### Run Tests
```bash
flutter test
```

### Build APK
```bash
flutter build apk --release
```

## 📝 Tasks

TASK-MB-001: ✅ Flutter Project Initialize

Detaylı task listesi için: `../../docs/TASKS.md`

## 👥 Team

- **Mobile Developer:** Mehmet Kurt
- **Backend Developer:** Emre Kayacan
