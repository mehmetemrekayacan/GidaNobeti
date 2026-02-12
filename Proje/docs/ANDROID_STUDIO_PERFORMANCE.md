# ⚡ Android Studio Performans İyileştirme

Android Studio ve emulator yavaş çalışıyorsa aşağıdaki ayarları yapın.

---

## 1. Emulator Performans Ayarları

### AVD (Android Virtual Device) Ayarları

1. **Android Studio** → **Device Manager** → Emulator'ün yanındaki **kalem ikonu** (Edit)
2. **Show Advanced Settings** → Aşağıdaki ayarları yapın:

**RAM:**
- **RAM:** 2048 MB veya 4096 MB (bilgisayarınızın RAM'ine göre)
- **VM heap:** 512 MB

**Graphics:**
- **Graphics:** **Hardware - GLES 2.0** (en hızlı)
- Eğer donuyorsa → **Automatic** veya **Software**

**Multi-core CPU:**
- **Number of processors:** 2 veya 4 (CPU çekirdek sayınıza göre)

**Cold Boot yerine Quick Boot:**
- **Boot option:** **Quick boot** (Cold boot yerine)

---

## 2. Android Studio Ayarları

### Memory Ayarları

1. **File** → **Settings** (Windows) veya **Android Studio** → **Preferences** (Mac)
2. **Appearance & Behavior** → **System Settings** → **Memory Settings**
3. **IDE memory:** 2048 MB veya 4096 MB
4. **Apply** → **OK** → Android Studio'yu yeniden başlatın

### Gradle Ayarları

1. **File** → **Settings** → **Build, Execution, Deployment** → **Build Tools** → **Gradle**
2. **Gradle JVM:** **JDK 17** veya **JDK 11** seçin
3. **Build and run using:** **Gradle** (IntelliJ IDEA yerine)
4. **Run tests using:** **Gradle**

### Android Studio Cache Temizleme

1. **File** → **Invalidate Caches / Restart**
2. **Invalidate and Restart** seçin

---

## 3. Emulator Alternatifleri

### Daha Hızlı Emulator: Genymotion veya BlueStacks

Eğer Android Studio emulator çok yavaşsa:

**Genymotion (Ücretsiz Personal Edition):**
- https://www.genymotion.com/
- Android Studio emulator'dan genelde daha hızlı

**BlueStacks (Android emulator):**
- https://www.bluestacks.com/
- ADB bağlantısı için ayar gerekir

---

## 4. Flutter Build Optimizasyonu

### Debug Build'i Hızlandırma

`flutter run` yerine:

```bash
flutter run --release
```

**Not:** Release modda hot reload çalışmaz, ama çok daha hızlıdır.

### Gradle Daemon

`android/gradle.properties` dosyasına ekleyin:

```properties
org.gradle.daemon=true
org.gradle.parallel=true
org.gradle.caching=true
org.gradle.configureondemand=true
```

---

## 5. Bilgisayar Performansı

### Windows

1. **Güç ayarları:** Yüksek performans modu
2. **Antivirus:** Android Studio ve proje klasörünü hariç tutun
3. **Disk alanı:** En az 10 GB boş alan
4. **RAM:** En az 8 GB önerilir (16 GB ideal)

### Emulator için Önerilen Sistem

- **CPU:** Intel i5 veya üzeri (veya AMD eşdeğeri)
- **RAM:** 16 GB
- **Disk:** SSD (HDD yerine)
- **GPU:** Hardware acceleration için desteklenen GPU

---

## 6. Hızlı Çözümler

### Emulator Çok Yavaşsa

1. **Emulator'ü kapatın**
2. **Android Studio'yu kapatın**
3. **Bilgisayarı yeniden başlatın**
4. **Sadece Android Studio'yu açın** (diğer programları kapatın)
5. **Emulator'ü başlatın** → **Quick boot** kullanın

### Build Çok Yavaşsa

```bash
cd Proje/mobile
flutter clean
flutter pub get
flutter run
```

### Gradle Build Cache Temizleme

```bash
cd Proje/mobile/android
./gradlew clean
```

Windows'ta:
```bash
cd Proje\mobile\android
gradlew.bat clean
```

---

## 7. Alternatif: Fiziksel Telefon Kullanma

Emulator yerine fiziksel Android telefon kullanabilirsiniz:

1. **Telefonda:** Ayarlar → Geliştirici seçenekleri → **USB debugging** açın
2. **USB ile bağlayın**
3. **Terminal:** `flutter devices` → telefonunuzu görmeli
4. **Flutter run:** Otomatik telefona yüklenir

**Avantajlar:**
- Çok daha hızlı
- Gerçek cihaz testi
- Kamera/galeri gerçek çalışır

**Dezavantajlar:**
- Her seferinde USB bağlantısı gerekir
- Backend'in yerel ağ IP'si gerekir (10.0.2.2 yerine)

---

## 8. Sorun Giderme

### Emulator Donuyor

- **Cold boot** yapın (Quick boot yerine)
- Emulator'ü yeniden başlatın
- RAM'i artırın (2048 → 4096 MB)

### Build Çok Uzun Sürüyor

- İlk build normal (Gradle indirmeleri)
- Sonraki build'ler daha hızlı olmalı
- Eğer her seferinde uzun sürüyorsa → Gradle cache temizleyin

### Android Studio Çöküyor

- Memory ayarlarını artırın (2048 MB → 4096 MB)
- Cache'i temizleyin (Invalidate Caches)
- Android Studio'yu güncelleyin

---

## Özet: En Hızlı Çözüm

1. **Emulator RAM:** 4096 MB
2. **Graphics:** Hardware - GLES 2.0
3. **Quick boot:** Açık
4. **Android Studio memory:** 4096 MB
5. **Gradle daemon:** Açık
6. **İlk build sonrası:** Sonraki build'ler hızlı olur

Eğer hala yavaşsa → **Fiziksel telefon** kullanın (en hızlı seçenek).
