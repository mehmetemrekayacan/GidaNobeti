# 🚀 Hızlı Başlatma Rehberi

## 1. Backend

```bash
cd Proje
docker-compose up -d
```

Kontrol: http://localhost:8000/health → `{"status":"healthy"}`

---

## 2. Admin Panel

```bash
cd Proje\admin-panel
npm install
npm run dev
```

Kontrol: http://localhost:3000

---

## 3. Mobil Uygulama

### Emulator ile

1. Android Studio → Virtual Device Manager → cihaz başlat (▶️)
2. Sonra:
   ```bash
   cd Proje\mobile
   flutter pub get
   flutter run --dart-define=API_BASE_URL=http://192.168.1.104:8000
   ```

### Fiziksel telefon ile

- Ortak ağlarda (okul, yurt, kurumsal ağ vb.) **AP Isolation** nedeniyle cihazlar arası iletişim kapalı olabilir.
- Bu yüzden fiziksel cihaz testinde en güvenli ve stabil yöntem: **USB üzerinden ADB Reverse tünelleme**.

1. Telefonu USB ile bağlayın (USB hata ayıklama açık), sonra:
   ```bash
   adb reverse tcp:8000 tcp:8000
   ```
2. Uygulamayı localhost üzerinden başlatın:
   ```bash
   cd Proje\mobile
   flutter run --dart-define=API_BASE_URL=http://127.0.0.1:8000
   ```

**Not:** Telefonu yeniden başlattığınızda veya USB bağlantısı koptuğunda `adb reverse` komutunu tekrar çalıştırın.

---

## Test Hesapları

| Rol     | TCKN         | Şifre    |
|--------|--------------|----------|
| Öğrenci| `12345678901`| `Test123!` |
| Admin  | '11111111111' |'Admin123!' |


adb reverse tcp:8000 tcp:8000