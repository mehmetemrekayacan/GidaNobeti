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
   flutter run
   ```

### Fiziksel telefon ile

- Telefon ve bilgisayar **aynı Wi‑Fi**’de olsun.
- Bilgisayar IP’si: `ipconfig` ile bakın (örn. 192.168.1.104).

**USB ile:** Telefonu takın, sonra:
```bash
cd Proje\mobile
flutter run --dart-define=API_HOST=192.168.1.104
```

**Wireless (USB şarj etmeden):**

1. Bir kez USB ile bağlayın (USB hata ayıklama açık), sonra:
   ```bash
   adb tcpip 5555
   ```
2. Telefon IP’sini bulun (Ayarlar → Wi‑Fi → ağ → IP).
3. USB’yi çekin:
   ```bash
   adb connect 192.168.1.101:5555
   ```
4. Uygulamayı çalıştırın (**mutlaka** bilgisayar IP'si ile, yoksa "connection timeout" alırsınız):
   ```bash
   cd Proje\mobile
   flutter run --dart-define=API_HOST=192.168.1.104
   ```
   `192.168.1.104` yerine kendi bilgisayar IP'nizi yazın (`ipconfig` ile bakın). Cihaz listesinde wireless cihaz seçilir.

**Not:** USB’yi sadece wireless’ı ilk kurarken veya **telefonu yeniden başlattıktan** sonra takmanız gerekir. Her bilgisayar açılışında aynı Wi‑Fi’deyse sadece `adb connect 192.168.1.101:5555` yeterli.

**Bağlantıyı kesmek:** `adb disconnect 192.168.1.101:5555` (bilgisayar artık o cihazı görmez; tekrar bağlanmak için `adb connect ...` yeterli).

---

## Test Hesapları

| Rol     | TCKN         | Şifre    |
|--------|--------------|----------|
| Öğrenci| `12345678901`| `Test123!` |
| Admin  | '11111111111' |'Admin123!' |
