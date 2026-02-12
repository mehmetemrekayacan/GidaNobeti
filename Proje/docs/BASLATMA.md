# 🚀 Hızlı Başlatma Rehberi

## 1. Backend Başlatma

```bash
cd Proje
docker-compose up -d
```

**Kontrol:** Tarayıcıda http://localhost:8000/health açılsın, `{"status":"healthy"}` görünsün.

---

## 2. Admin Panel Başlatma

```bash
cd Proje\admin-panel
npm install
npm run dev
```

**Kontrol:** Tarayıcıda http://localhost:3000 açılsın.

---

## 3. Mobil Uygulama Başlatma

### Önce Android emulator başlat:
1. **Android Studio** → **Virtual Device Manager**
2. Bir cihaz seçip **▶️** ile başlat

### Sonra mobil uygulamayı çalıştır:

```bash
cd Proje\mobile
flutter pub get
flutter run
```

**Not:** İlk seferde Gradle indirmeleri birkaç dakika sürebilir.

---

## Test Hesapları

**Öğrenci:**
- TCKN: `12345678901`
- Şifre: `Test123!`

**Admin:** (Backend seed script'inden gelir)
