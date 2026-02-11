# 📱 Mobil Uygulama Nasıl Çalıştırılır (Android Studio)

**Gereksinimler:** Flutter kurulu, Android Studio kurulu, Backend (Docker) çalışıyor.

---

## 1. Flutter kurulumu

Terminalde kontrol edin:

```bash
flutter --version
```

Çıktı örnek: `Flutter 3.x.x • channel stable`

- Flutter yüklü değilse: https://docs.flutter.dev/get-started/install/windows  
- Kurulumdan sonra: `flutter doctor` çalıştırıp Android toolchain’in “OK” olduğundan emin olun.

---

## 2. Backend’in çalıştığından emin olun

Mobil uygulama API’ye istek atacak. Önce backend ayakta olmalı:

```bash
cd Proje
docker-compose up -d
```

Kontrol: Tarayıcıda **http://localhost:8000/health** açılsın, `{"status":"healthy"}` görünsün.

---

## 3. Android emulator (Android Studio)

1. **Android Studio**’yu açın.
2. **More Actions** → **Virtual Device Manager** (veya **Tools** → **Device Manager**).
3. Listede bir cihaz varsa yanındaki **▶️ (Play)** ile başlatın.
4. Cihaz yoksa **Create Device** → örn. **Pixel 6** → **Next** → bir sistem imajı seçip (örn. API 34) indirin → **Finish** → sonra **▶️** ile başlatın.
5. Emulator tam açılsın (birkaç dakika sürebilir).

Terminalden de başlatabilirsiniz:

```bash
flutter emulators
flutter emulators --launch <emulator_id>
```

Çalışan cihazları görmek için:

```bash
flutter devices
```

“sdk gphone” veya “emulator-5554” gibi bir satır görünmeli.

---

## 4. Mobil uygulamayı çalıştırma

**Yeni bir terminal** açın:

```bash
cd Proje\mobile
flutter pub get
flutter run
```

- Birden fazla cihaz/emulator varsa Flutter hangi cihaza yükleneceğini sorar; Android emulator’ü seçin (genelde listede numarayla gösterilir).
- Sadece bir Android emulator açıksa doğrudan ona yüklenir.

Belirli cihaza yüklemek için:

```bash
flutter run -d emulator-5554
```

(Cihaz ID’sini `flutter devices` çıktısından alın.)

İlk çalıştırmada Gradle indirmeleri birkaç dakika sürebilir. Sonrasında uygulama emulator’de açılır.

---

## 5. API adresi (önemli)

- **Android emulator** içinden `localhost` sizin bilgisayarınızı göstermez. Bu yüzden projede Android için **http://10.0.2.2:8000** kullanılıyor (emulator’ün bilgisayara erişim adresi).
- Backend’i **localhost:8000**’de çalıştırdığınız sürece emulator’den bu adresle erişilir; ekstra ayar gerekmez.
- **Fiziksel telefon** ile test edecekseniz: backend’in çalıştığı bilgisayarın **yerel ağ IP’si** (örn. `192.168.1.5:8000`) gerekir; bu durumda `lib/core/api/dio_client.dart` içindeki base URL’i buna göre değiştirmeniz gerekir.

---

## 6. Test girişi (öğrenci)

Backend’de seed verisi varsa örnek öğrenci:

- **TCKN:** `12345678901`  
- **Şifre:** `Test123!`

(Seed script: `docker exec -it gidanobeti_api python seed_restaurants.py`)

---

## Kısa özet (Android Studio + emulator)

1. Docker: `docker-compose up -d`
2. Android Studio: Virtual Device Manager’dan emulator’ü ▶️ ile başlat.
3. `cd Proje\mobile` → `flutter pub get` → `flutter run`
4. Emulator’de uygulama açılır; giriş ekranında yukarıdaki TCKN/şifre ile deneyin.

---

## Sık karşılaşılan sorunlar

| Sorun | Çözüm |
|--------|--------|
| `flutter: command not found` | Flutter’ı kurun ve PATH’e ekleyin. |
| `No devices found` | Android Studio’dan bir emulator başlatın; `flutter devices` ile kontrol edin. |
| Uygulama “Connection refused” / API’ye ulaşamıyor | Backend’in çalıştığını (http://localhost:8000/health) ve Android için `10.0.2.2:8000` kullanıldığını kontrol edin. |
| Gradle / build çok uzun sürüyor | İlk seferde normal; sonraki çalıştırmalar daha hızlı olur. |
| Emulator çok yavaş | AVD’de “Cold boot” yerine “Quick boot” kullanın; RAM’i artırın. |

Detaylı sorun giderme: `docs/DEMO_FIXES.md` ve `docs/GELISTIRME_ORTAMI.md`.

### Sipariş Yükle: Kamera ve galeri (emulator)

- **Kamera çalışmıyor:** Emulator'de kamera varsayılan olarak sanal/boş olabilir. Device Manager'da cihazı **düzenle** (kalem ikonu) → **Advanced Settings** → **Camera**: **Webcam** (bilgisayar kameranız) veya **Virtual scene** seçin. Kaydedip emulator'ü yeniden başlatın. Alternatif: sadece **Galeriden seç** kullanın.

- **Emulator galeriye fotoğraf ekleme (detaylı):**  
  Sürükleyip bırakınca "Copied" / "Saved" görünür ama **Galeri uygulaması** bazen bu dosyayı hemen göstermez; dosya **Downloads** klasörüne iner. Aşağıdaki iki yöntemden birini kullanın.

---

#### Yöntem A: Uygulamada "Galeriden seç" derken **Downloads / Dosyalar**’a bak

1. Bilgisayardan bir **.jpg** veya **.png** dosyasını emulator penceresine **sürükleyip bırakın**. "Copied" / "File saved" gibi bir mesaj çıkabilir.
2. **Gıda Nöbeti** uygulamasını açın → **Sipariş Yükle** → **Galeriden seç**.
3. Açılan seçici ekranda **sadece "Galeri" / "Photos" sekmesine bakmayın**. Üstte veya altta şunlara tıklayın:
   - **Downloads** (İndirilenler)
   - **Files** / **Dosyalar**
   - **Browse** / **Gözat**
   - Bazen **⋮** (üç nokta) menüsünde **"Show internal storage"** / **"Downloads"** olur.
4. **Downloads** (veya **Internal storage** → **Download**) klasörüne girince sürüklediğiniz resim orada listelenir. Ona dokunup seçin.
5. Seçince uygulama yüklemeye geçer.

---

#### Yöntem B: Önce Files ile bul, sonra uygulamada seç

1. Sürükleyip bıraktıktan sonra emulator’de **Files** (Dosyalar) veya **Downloads** uygulamasını açın. (App drawer’da "Files", "Files by Google" veya "Downloads" arayın.)
2. **Downloads** (İndirilenler) klasörüne girin. Sürüklediğiniz resim burada görünür.
3. Resme dokunup açın (önizleme açılır). İsterseniz bu ekranda **⋮** → **Save to Photos** / **Galeriye kaydet** varsa onu kullanın; böylece resim "Galeri"de de görünür.
4. **Gıda Nöbeti**’ne dönün → **Sipariş Yükle** → **Galeriden seç**. Açılan seçicide:
   - **Downloads** veya **Files** sekmesine girin,
   - Az önce gördüğünüz resmi seçin.

---

#### Hâlâ görünmüyorsa

- Sürüklerken dosyanın **emulator penceresinin ortasına** (ekran alanına) bırakıldığından emin olun.
- Emulator’ü **yeniden başlatıp** (▶ Stop, sonra ▶ Play) sürükle-bırakı tekrar deneyin.
- **Settings** → **Apps** → **Files** (veya **Downloads**) → **Storage** → **Clear cache** yapıp tekrar **Files / Downloads** içinde **Downloads** klasörüne bakın.
- Alternatif: Emulator’de **Chrome**’u açıp bir fiş görseli arayın, görsele uzun basıp **"Download image"** / **"Resmi indir"** deyin; dosya yine **Downloads**’a iner. Sonra uygulamada **Galeriden seç** → **Downloads**’tan bu resmi seçin.

---

## Mobil Faz 2 Özellikleri (Şubat 2026)

- **Giriş:** Login/Register; oturum saklanır (uygulama kapatılsa bile giriş kalır).
- **Ana sayfa:** Risk Panosu (riskli restoranlar listesi), Hızlı İşlemler (Restoranlar, Riskli Restoranlar, Sipariş Yükle, Geçmiş).
- **Sipariş Yükle:** Kamera veya galeriden fiş fotoğrafı → OCR ile yükleme; risk uyarıları gösterilir.
- **Sipariş Geçmişi:** Kendi siparişlerin listesi (sayfalama).
- **Riskli Restoranlar:** Tam liste ekranı + ana sayfada özet.
