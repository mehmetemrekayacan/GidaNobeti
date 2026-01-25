# 🔧 DEMO HAZIRLIK - HATA ÇÖZÜMLERİ

## ✅ Çözülen Sorunlar

### 1. Backend Seed Script Hatası
**Sorun:** `ModuleNotFoundError: No module named 'sqlalchemy'`

**Çözüm:** Seed script'i Docker container içinde çalıştırın:
```bash
docker exec -it gidanobeti_api python seed_restaurants.py
```

### 2. Admin Panel Eksik Dependencies
**Sorun:** `Module not found: Can't resolve 'axios'`

**Çözüm:** 
- ✅ `axios` package.json'a eklendi
- Şimdi şunu çalıştırın:
```bash
cd Proje/admin-panel
npm install
npm run dev
```

### 3. Login 422 Validation Hatası
**Sorun:** Admin panel'de login yaparken `422 Unprocessable Entity` hatası ve React render hatası

**Çözüm:**
- ✅ Frontend'de error handling düzeltildi (validation error array'lerini parse ediyor)
- ✅ TCKN input'undan boşluklar temizleniyor
- ✅ Backend'de `LoginRequest` schema'sına TCKN validator eklendi
- ✅ Backend'i yeniden başlatın (schema değişti):
```bash
docker-compose restart gidanobeti_api
```

**Test:**
- TCKN: `11111111111`
- Şifre: `Admin123!`

### 4. "Bu panel sadece yöneticiler içindir" Hatası
**Sorun:** Login başarılı ama kullanıcı `STUDENT` rolünde. Admin paneli için `DORM_MANAGER` rolü gerekli.

**Çözüm:**
- ✅ Seed script güncellendi - mevcut admin kullanıcısının rolünü kontrol edip `DORM_MANAGER` yapıyor
- Seed script'i tekrar çalıştırın:
```bash
docker exec -it gidanobeti_api python seed_restaurants.py
```

**Beklenen Çıktı:**
```
✅ Admin user already exists (TCKN: 11111111111)
   ⚠️ Admin role is STUDENT, updating to DORM_MANAGER...
   ✅ Admin role and status updated
```

**Kontrol:**
- Swagger'da login yapın (TCKN: `11111111111`, Password: `Admin123!`)
- Response'daki `user.role` alanının `DORM_MANAGER` olduğunu kontrol edin

### 5. Student Login Sorunu
**Sorun:** Student kullanıcısı giriş yapamıyor (mobile app veya Swagger'da).

**Çözüm:**
- ✅ Seed script güncellendi - student kullanıcısının `is_active` ve `is_verified` durumunu kontrol edip güncelliyor
- Seed script'i tekrar çalıştırın:
```bash
docker exec -it gidanobeti_api python seed_restaurants.py
```

**Beklenen Çıktı:**
```
✅ Student user already exists (TCKN: 12345678901)
   ✅ Student password is correct
   ✅ Student account is active and verified
```

**Test:**
- Swagger'da login yapın: TCKN=`12345678901`, Password=`Test123!`
- Response'da `user.role` alanının `STUDENT` olduğunu kontrol edin
- Mobile app'te de aynı bilgilerle login deneyin

### 6. Mobile App Çalıştırma
**Sorun:** Mobile app nasıl çalıştırılır?

**Çözüm:**
1. **Dependencies yükle:**
```bash
cd Proje/mobile
flutter pub get
```

2. **Code generation çalıştır (Retrofit için):**
```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

3. **Emulator başlat ve uygulamayı çalıştır:**
```bash
flutter run
```

**Önemli Notlar:**
- **Android Emulator:** API base URL otomatik olarak `http://10.0.2.2:8000` olarak ayarlanmış
- **iOS Simulator:** API base URL `http://localhost:8000` kullanıyor
- Backend'in çalıştığından emin olun (`docker-compose ps`)

**Test Kullanıcıları:**
- TCKN: `12345678901`
- Şifre: `Test123!`

**Sorun Giderme:**
- "Connection refused" hatası alırsanız:
  - Backend'in çalıştığını kontrol edin (`docker-compose ps`)
  - Android emulator için `10.0.2.2:8000` kullanıldığını kontrol edin

### 7. Android Emulator Başlatma
**Sorun:** Android Studio'da emulator nasıl başlatılır?

**Çözüm:**

**Yöntem 1: Android Studio GUI (Önerilen)**
1. Android Studio'yu açın
2. Sağ üst köşede **"Device Manager"** (cihaz simgesi) tıklayın
3. Eğer emulator yoksa:
   - **"Create Device"** butonuna tıklayın
   - **Phone** kategorisinden bir cihaz seçin (örn: Pixel 5)
   - **System Image** seçin (API 33 veya 34 önerilir)
   - **Finish** tıklayın
4. Emulator listesinde **▶️ (Play)** butonuna tıklayın
5. Emulator açıldıktan sonra Flutter uygulamasını çalıştırın

**Yöntem 2: Komut Satırı**
```bash
# Emulator listesini göster
flutter emulators

# Belirli bir emulator'ü başlat (PowerShell'de tırnak içinde)
flutter emulators --launch "Medium_Phone_API_36.1"

# Veya Android Studio'nun emulator'ünü doğrudan başlat
cd %LOCALAPPDATA%\Android\Sdk\emulator
emulator -avd Medium_Phone_API_36.1
```

**Önemli:** PowerShell'de `<emulator_id>` yerine gerçek emulator ID'sini kullanın (tırnak içinde).

**Kontrol:**
```bash
# Çalışan cihazları kontrol et
flutter devices
```

### 8. Build Runner Hatası (Retrofit Versiyon Uyumsuzluğu)
**Sorun:** `build_runner` çalıştırırken `Parser.DartMappable` hatası alınıyor.

**Çözüm:**
Bu hata Retrofit ve retrofit_generator versiyonları arasındaki uyumsuzluktan kaynaklanıyor. **Şimdilik build_runner'a gerek yok** çünkü projede DioClient kullanılıyor, Retrofit kullanılmıyor.

**Geçici Çözüm (Build Runner Olmadan):**
```bash
# Build runner olmadan direkt çalıştır
flutter run
```

**Kalıcı Çözüm (İleride gerekirse):**
```bash
# pubspec.yaml'da versiyonları güncelle
# retrofit: ^4.4.1 → retrofit: ^4.9.2
# retrofit_generator: ^9.1.4 → retrofit_generator: ^10.2.1

# Sonra tekrar dene
flutter pub get
dart run build_runner build --delete-conflicting-outputs
```

**Not:** Şu anda Retrofit kullanılmadığı için build_runner olmadan da uygulama çalışacaktır.

### 9. Emulator Google Play Store Açılıyor / Geri Butonu Çalışmıyor
**Sorun:** Emulator açıldığında Google Play Store açılıyor ve geri butonu çalışmıyor.

**Çözüm:**

**Yöntem 1: Home Butonuna Bas**
- Emulator'ün sağ tarafındaki kontrol panelinde **Home** butonuna (daire simgesi) basın
- Bu sizi ana ekrana götürecektir

**Yöntem 2: Emulator'ü Yeniden Başlat**
- Emulator'ü kapatın (X butonu veya kapat)
- Android Studio'dan tekrar başlatın
- İlk açılışta Google Play Store açılabilir, bu normaldir

**Yöntem 3: Flutter Uygulamasını Doğrudan Çalıştır**
- Emulator açıkken terminal'de:
```bash
flutter run -d emulator-5554
```
- Bu komut emulator'ü bulup uygulamayı otomatik başlatacaktır

**Yöntem 4: Emulator'ün Tamamen Açılmasını Bekle**
- Emulator açıldıktan sonra 10-15 saniye bekleyin
- Android'in tamamen yüklenmesini bekleyin
- Sonra `flutter devices` ile kontrol edin, online olmalı

### 10. Emulator Offline Görünüyor
**Sorun:** `flutter devices` komutu emulator'ü offline gösteriyor.

**Çözüm:**

1. **Emulator'ün Tamamen Açılmasını Bekleyin**
   - Emulator açıldıktan sonra Android'in tamamen yüklenmesini bekleyin (30-60 saniye)
   - Lock screen'i açın (gerekirse swipe up)

2. **ADB Bağlantısını Kontrol Edin**
```bash
# ADB cihazları listele
adb devices

# Eğer unauthorized görünüyorsa, emulator'de "Allow USB debugging" onaylayın
# Eğer offline görünüyorsa:
adb kill-server
adb start-server
adb devices
```

3. **Emulator'ü Yeniden Başlatın**
   - Emulator'ü tamamen kapatın
   - Android Studio'dan tekrar başlatın
   - Tamamen açıldıktan sonra `flutter devices` çalıştırın

### 11. Windows Symlink Hatası
**Sorun:** Windows'ta Flutter çalıştırırken "Building with plugins requires symlink support" hatası.

**Çözüm:**

**Windows Developer Mode'u Açın:**
1. Windows Ayarlarını açın: `start ms-settings:developers`
2. **Developer Mode** seçeneğini **Açık** yapın
3. Uyarıyı onaylayın
4. Terminal'i yeniden başlatın
5. `flutter run` komutunu tekrar çalıştırın

**Alternatif: Yönetici Olarak Çalıştır**
- PowerShell'i **Yönetici olarak çalıştır** (sağ tık → Run as administrator)
- Sonra `flutter run` komutunu çalıştırın

**Not:** Android emulator kullanmak daha iyi olur, Windows desktop'ta bazı plugin'ler çalışmayabilir.

### 12. Emulator Donmuş / Hiçbir Tuş Çalışmıyor
**Sorun:** Emulator açıldığında Google Play Store'da takılı kalıyor ve hiçbir tuş çalışmıyor (geri, home, sign in).

**Çözüm:**

**Yöntem 1: Emulator'ü Cold Boot ile Yeniden Başlat (Önerilen)**
1. Emulator'ü tamamen kapatın (X butonu)
2. Android Studio'da **Device Manager**'ı açın
3. Emulator'ün yanındaki **▼ (dropdown)** butonuna tıklayın
4. **"Cold Boot Now"** seçeneğini seçin
5. Bu emulator'ü temiz bir durumdan başlatacaktır

**Yöntem 2: Emulator'ü Wipe Data ile Başlat**
1. Emulator'ü kapatın
2. Android Studio → Device Manager
3. Emulator'ün yanındaki **▼** → **"Wipe Data"**
4. Onaylayın
5. Emulator'ü tekrar başlatın (▶️ butonu)

**Yöntem 3: Yeni Emulator Oluştur**
1. Android Studio → Device Manager
2. **"Create Device"** tıklayın
3. **Phone** → **Pixel 5** seçin
4. **System Image:** API 33 (Android 13) veya API 34 (Android 14) seçin
5. **Finish** tıklayın
6. Yeni emulator'ü başlatın

**Yöntem 4: Emulator'ü Komut Satırından Kapat**
```powershell
# ADB PATH'te değilse, tam yolu kullanın:
# Genellikle: %LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe

# Tüm emulator'leri kapat
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" emu kill

# Veya Android Studio'dan kapatın (Daha Kolay):
# 1. Emulator penceresini kapatın (X butonu)
# 2. Veya Android Studio → Device Manager → Emulator'ün yanındaki ▼ → "Stop"
```

**Yöntem 5: Flutter Uygulamasını Doğrudan Çalıştır (Emulator Açıkken)**
- Emulator açıkken (Google Play Store'da bile olsa), terminal'de:
```powershell
flutter run -d emulator-5554
```
- Bu komut uygulamayı doğrudan yükleyip başlatacaktır

**Önerilen Çözüm:**
1. Emulator'ü kapatın (`adb emu kill` veya X butonu)
2. Android Studio → Device Manager → **"Cold Boot Now"**
3. Emulator açıldıktan sonra 30 saniye bekleyin
4. `flutter devices` ile kontrol edin
5. `flutter run` ile uygulamayı başlatın

### 13. Uygulama Build Tamamlandı Ama Görünmüyor
**Sorun:** Flutter build tamamlandı ama uygulama emulator'de görünmüyor veya açılmıyor.

**Çözüm:**

**Yöntem 1: Uygulamayı Manuel Olarak Aç**
1. Emulator'de **App Drawer**'ı açın (aşağı kaydırın veya home screen'de yukarı kaydırın)
2. **"mobile"** adlı uygulamayı arayın
3. Uygulamaya tıklayarak açın

**Yöntem 2: ADB ile Uygulamayı Başlat**
```powershell
# ADB PATH'te değilse tam yolu kullanın
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" shell am start -n tr.gov.gidanobeti.mobile/.MainActivity
```

**Yöntem 3: Flutter Run Komutunu Tekrar Çalıştır**
```powershell
# Emulator'ü belirterek çalıştır
flutter run -d emulator-5554
```

**Yöntem 4: Uygulamanın Yüklü Olduğunu Kontrol Et**
```powershell
# Yüklü uygulamaları listele
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" shell pm list packages | Select-String "gidanobeti"

# Eğer görünüyorsa, uygulama yüklü demektir
```

**Yöntem 5: Uygulamayı Yeniden Yükle**
```powershell
# Uygulamayı kaldır
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" uninstall tr.gov.gidanobeti.mobile

# Tekrar yükle ve çalıştır
flutter run -d emulator-5554
```

**Not:** Uygulama adı "mobile" olarak görünebilir (AndroidManifest.xml'de `android:label="mobile"`). App Drawer'da "mobile" veya "Gıda Nöbeti" olarak arayın.

---

## 🚀 GÜNCEL ADIMLAR

### Adım 1: Backend'i Başlat ✅
```bash
cd Proje
docker-compose up -d
```

### Adım 2: Seed Data'yı Yükle (DÜZELTİLDİ)
```bash
# Docker container içinde çalıştır
docker exec -it gidanobeti_api python seed_restaurants.py
```

**Alternatif (Local Python):**
```bash
cd Proje/backend
pip install -r requirements.txt
python seed_restaurants.py
```

### Adım 3: Admin Panel'i Başlat (DÜZELTİLDİ)
```bash
cd Proje/admin-panel
npm install  # axios eklendi, tekrar yükle
npm run dev
```

---

## ⚠️ Eğer Hala TailwindCSS Hatası Alırsanız

TailwindCSS v4 kullanılıyor ve config doğru. Eğer hala hata alırsanız:

```bash
cd Proje/admin-panel
rm -rf node_modules package-lock.json
npm install
npm run dev
```

Veya Next.js cache'i temizleyin:
```bash
cd Proje/admin-panel
rm -rf .next
npm run dev
```

---

## ✅ BAŞARILI ÇALIŞMA KONTROLÜ

1. **Backend:**
   - http://localhost:8000/health → `{"status":"healthy",...}`
   - http://localhost:8000/docs → Swagger UI açılmalı

2. **Seed Data:**
   - Container içinde seed script çalıştı
   - "✅ Seeded 10 test restaurants" mesajı görünmeli

3. **Admin Panel:**
   - http://localhost:3000 → Login sayfası açılmalı
   - Hata mesajı olmamalı

---

**Son Güncelleme:** 25 Ocak 2026
