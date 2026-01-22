# Gıda Nöbeti - Mobile App

Flutter mobil uygulama projesi.

## 🚀 Başlangıç

### Gereksinimler
- Flutter 3.38.7+
- Dart 3.10.7+
- Android Studio (Android development için)
- Xcode (iOS development için - Mac)

### Kurulum

1. **Dependencies yükle:**
```bash
flutter pub get
```

2. **Uygulamayı çalıştır:**
```bash
flutter run
```

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
