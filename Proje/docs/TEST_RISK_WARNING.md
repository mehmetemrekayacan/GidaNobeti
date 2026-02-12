# 🧪 Risk Warning Dialog Test Senaryosu

**Task:** TASK-MB-012 - Risk Warning Dialog  
**Amaç:** Riskli restoran uyarısı dialog'unun doğru çalıştığını test etmek

---

## Ön Koşullar

1. ✅ Backend çalışıyor (`docker-compose up -d`)
2. ✅ Admin panel çalışıyor (`npm run dev` → http://localhost:3000)
3. ✅ Mobil uygulama çalışıyor (`flutter run`)
4. ✅ Öğrenci hesabı ile giriş yapılmış (TCKN: `12345678901`, Şifre: `Test123!`)

---

## Senaryo 1: Admin Panel ile Restoranı Riskli Yap

### Adım 1: Admin Panel'e Giriş

1. Tarayıcıda http://localhost:3000 açın
2. Admin hesabı ile giriş yapın (backend seed'den admin hesabı)

### Adım 2: Restoranı RED_FLAG Yap

1. Sol menüden **"Restoranlar"** sayfasına gidin
2. Listede bir restoran bulun (veya yeni bir sipariş yükleyerek restoran oluşturun)
3. Restoran satırında **"Düzenle"** butonuna tıklayın
4. **Risk Durumu** dropdown'ından **"RED_FLAG"** seçin
5. **Risk Nedeni** alanına örn. `"Son 24 saatte 3+ şikayet alındı"` yazın
6. **Kaydet** butonuna basın

**Beklenen:** Restoran risk durumu RED_FLAG olarak güncellenir.

---

## Senaryo 2: API ile Restoranı Riskli Yap (Alternatif)

Eğer admin panel kullanmak istemiyorsanız, direkt API ile:

```bash
# Önce admin token alın
curl -X POST http://localhost:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"tckn":"<admin_tckn>","password":"<admin_password>"}'

# Token'ı kullanarak restoranı RED_FLAG yapın
curl -X PUT "http://localhost:8000/v1/admin/restaurants/<restaurant_id>/risk-status?new_status=RED_FLAG&reason=Test%20i%C3%A7in%20riskli%20yap%C4%B1ld%C4%B1" \
  -H "Authorization: Bearer <access_token>"
```

**Not:** `<restaurant_id>` yerine gerçek restoran ID'sini yazın (ör. `1`, `2`).

---

## Senaryo 3: Mobil Uygulamada Riskli Restorandan Sipariş Yükle

### Adım 1: Sipariş Yükle Ekranına Git

1. Mobil uygulamada ana sayfadan **"Sipariş Yükle"** kartına dokunun
2. Veya sol üst menüden **"Sipariş Yükle"** seçeneğini açın

### Adım 2: Fiş Fotoğrafı Yükle

1. **"Kamera ile çek"** veya **"Galeriden seç"** butonuna dokunun
2. **Riskli yaptığınız restoranın fiş fotoğrafını** seçin/yükleyin
   - **Önemli:** Fiş üzerinde restoran adı, OCR tarafından okunabilir olmalı
   - Eğer fiş yoksa: Bilgisayardan bir fiş görseli indirip emulator'e sürükleyin (MOBILE_RUN.md'deki galeri ekleme yöntemi)

### Adım 3: Upload Sonrası Dialog Kontrolü

**Beklenen Sonuç:**

1. ✅ Upload başarılı mesajı görünür (yeşil kart: "Sipariş kaydedildi")
2. ✅ **Otomatik olarak kırmızı Risk Warning Dialog açılır:**
   - ⚠️ DİKKAT başlığı
   - Kırmızı alert tasarımı
   - Warning icon (Icons.warning_amber_rounded)
   - "Bu restoran denetim altında!" mesajı
   - Restoran adı gösterilir
   - Risk nedeni gösterilir (eğer varsa)
   - "Tamam" butonu

3. ✅ **"Tamam"** butonuna dokununca dialog kapanır

---

## Senaryo 4: Riskli Olmayan Restorandan Sipariş Yükle (Negatif Test)

### Adım 1: Normal Restorandan Sipariş Yükle

1. Risk durumu **SAFE** olan bir restoranın fişini yükleyin
2. Upload başarılı olur

**Beklenen:** 
- ✅ Yeşil başarı kartı görünür
- ❌ **Risk Warning Dialog açılmaz** (warnings listesi boş)

---

## Senaryo 5: WATCHLIST Restoranı Test

### Adım 1: Restoranı WATCHLIST Yap

Admin panel veya API ile bir restoranı **WATCHLIST** durumuna getirin.

### Adım 2: Sipariş Yükle

WATCHLIST restoranından sipariş yükleyin.

**Beklenen:**
- Backend'de WATCHLIST restoranları için de warning gönderilir mi kontrol edin
- Eğer gönderiliyorsa dialog açılmalı

---

## Hata Senaryoları

### 401 Unauthorized - Token Expired

**Belirtiler:**
- API istekleri 401 hatası veriyor: "Invalid or expired token"
- Uygulama logout olmuyor, hala authenticated görünüyor

**Çözüm:**
- ✅ **Düzeltildi:** 401 hatası geldiğinde otomatik logout yapılıyor
- Token expire olduğunda AuthBloc'a logout event'i gönderiliyor
- Kullanıcı login ekranına yönlendiriliyor

**Test:**
1. Uygulamaya giriş yapın
2. Token'ın expire olmasını bekleyin (backend'de JWT expire süresi kontrol edin)
3. Herhangi bir API isteği yapın (örn. Sipariş Yükle)
4. **Beklenen:** Otomatik logout olup login ekranına yönlendirilmeli

**Manuel Test (Token'ı expire etmek için):**
```bash
# Backend'de token expire süresini kısaltın veya
# SharedPreferences'tan token'ı manuel silin (debug için)
```

### Dialog Açılmıyor

**Olası Nedenler:**
1. Backend'den `warnings` listesi boş geliyor
   - **Çözüm:** Backend loglarını kontrol edin (`docker logs gidanobeti_api`)
   - Restoranın `current_risk_status` değerini kontrol edin (RED_FLAG veya BLACKLISTED olmalı)

2. Warning mesajı parse edilemiyor
   - **Çözüm:** Backend'den gelen warning formatını kontrol edin
   - Format: `"Dikkat: {restaurant_name} riskli restoran listesinde!"` olmalı

3. Dialog gösterilmeden önce sayfa yenileniyor
   - **Çözüm:** `WidgetsBinding.instance.addPostFrameCallback` kullanıldığından emin olun

### Dialog Tasarımı Bozuk

- Kırmızı renkler görünmüyor → `Colors.red.shade50`, `Colors.red.shade700` kullanıldığından emin olun
- Warning icon görünmüyor → `Icons.warning_amber_rounded` import edildiğinden emin olun

---

## API Test (Backend Doğrulama)

Backend'in doğru warning gönderdiğini test etmek için:

```bash
# Öğrenci token alın
TOKEN=$(curl -s -X POST http://localhost:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"tckn":"12345678901","password":"Test123!"}' | jq -r '.access_token')

# Sipariş yükle (multipart/form-data)
curl -X POST http://localhost:8000/v1/orders/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "image=@/path/to/receipt.jpg"

# Response'da warnings listesini kontrol edin:
# {
#   "order_id": "...",
#   "restaurant_name": "Riskli Restoran",
#   "warnings": ["Dikkat: Riskli Restoran riskli restoran listesinde!"],
#   ...
# }
```

**Beklenen:** `warnings` listesi boş olmamalı ve riskli restoran mesajı içermeli.

---

## Başarı Kriterleri

- ✅ Riskli restorandan sipariş yüklendiğinde dialog otomatik açılır
- ✅ Dialog tasarımı görsel olarak çarpıcıdır (kırmızı alert)
- ✅ Restoran adı ve risk nedeni doğru gösterilir
- ✅ "Tamam" butonu dialog'u kapatır
- ✅ Riskli olmayan restorandan sipariş yüklendiğinde dialog açılmaz

---

## Notlar

- **"İade Destek Kartı" butonu:** Henüz implement edilmedi (future task)
- **Dialog dismiss:** `barrierDismissible: false` olduğu için sadece "Tamam" butonu ile kapanır
- **Warning parse:** Backend'den gelen mesaj formatı değişirse parse logic güncellenmeli
