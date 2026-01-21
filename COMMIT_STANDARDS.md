# 📝 COMMIT STANDARTLARI

**Proje:** Gıda Nöbeti  
**Tarih:** 21 Ocak 2026

---

## 🎯 Genel İlkeler

- ✅ **Türkçe** commit mesajları
- ✅ **Kısa ve öz** (max 50 karakter başlık)
- ✅ **Net ve anlaşılır** (ne yapıldığını açıkça belirt)
- ✅ **Tek sorumluluk** (her commit tek bir şey yapmalı)
- ❌ "deneme", "test", "update" gibi belirsiz mesajlardan kaçın

---

## 📋 Commit Formatı

```
[KATEGORİ] Kısa açıklama

(Opsiyonel) Detaylı açıklama:
- Ne değişti?
- Neden değişti?
- Varsa ilgili task numarası
```

### Kategori Örnekleri:

| Kategori | Ne zaman kullan? | Örnek |
|----------|------------------|-------|
| `[FEAT]` | Yeni özellik | `[FEAT] OCR servis entegrasyonu tamamlandı` |
| `[FIX]` | Bug düzeltme | `[FIX] Login JWT token hatası düzeltildi` |
| `[REFACTOR]` | Kod iyileştirme | `[REFACTOR] Order servis kodları temizlendi` |
| `[DOCS]` | Dokümantasyon | `[DOCS] API endpoint dokümantasyonu eklendi` |
| `[STYLE]` | Formatlama | `[STYLE] Backend kodları formatlandı` |
| `[TEST]` | Test ekleme | `[TEST] OCR unit testleri eklendi` |
| `[CHORE]` | Altyapı/config | `[CHORE] Docker Compose dosyası oluşturuldu` |
| `[PERF]` | Performans | `[PERF] Database sorgu optimizasyonu` |
| `[SECURITY]` | Güvenlik | `[SECURITY] JWT secret key güçlendirildi` |

---

## ✅ İyi Örnekler

```bash
# Kısa ve net
git commit -m "[FEAT] Kullanıcı kayıt endpoint'i eklendi"

# Task referanslı
git commit -m "[FEAT] Sipariş yükleme ekranı (TASK-MB-009)"

# Detaylı açıklama
git commit -m "[FIX] OCR Türkçe karakter sorunu düzeltildi

- EasyOCR encoding hatası giderildi
- Ş, Ğ, İ karakterleri artık doğru okunuyor
- Test: 10 farklı fiş ile doğrulandı
"

# Birden fazla değişiklik
git commit -m "[CHORE] Backend altyapı kurulumu

- Docker Compose dosyası oluşturuldu
- PostgreSQL ve Redis servisleri eklendi
- FastAPI scaffold yapılandırıldı
- .env.example dosyası eklendi
"
```

---

## ❌ Kötü Örnekler

```bash
# ❌ Belirsiz
git commit -m "update"
git commit -m "deneme"
git commit -m "fix"

# ❌ İngilizce
git commit -m "[FEAT] Add user registration"

# ❌ Çok uzun başlık (50 karakteri aşıyor)
git commit -m "[FEAT] Kullanıcı kayıt sistemi ve email doğrulama mekanizması tamamen yeniden yazıldı"

# ❌ Birden fazla sorumluluk
git commit -m "[FEAT] Login eklendi, database güncellendt, test yazıldı"
```

---

## 🔄 Git Workflow

### 1️⃣ Değişiklikleri Kontrol Et
```bash
git status
git diff
```

### 2️⃣ Dosyaları Stage'le
```bash
# Tüm dosyalar
git add .

# Belirli dosyalar
git add backend/app/services/ocr_service.py
```

### 3️⃣ Commit Yap
```bash
# Basit commit
git commit -m "[FEAT] OCR servis eklendi"

# Detaylı commit (editör açılır)
git commit

# Editörde şöyle yaz:
# [FEAT] OCR servis eklendi
#
# - EasyOCR entegrasyonu tamamlandı
# - Türkçe ve İngilizce dil desteği
# - RAM-only processing (KVKK uyumlu)
```

### 4️⃣ Push Et
```bash
# İlk push (branch'i upstream'e bağla)
git push -u origin main

# Sonraki push'lar
git push
```

---

## 🌿 Branch İsimlendirme

```bash
# Feature branch
git checkout -b feature/ocr-service
git checkout -b feature/login-screen

# Bugfix branch
git checkout -b fix/jwt-token-error
git checkout -b fix/ocr-turkish-chars

# Task bazlı
git checkout -b task/BE-008-ocr-integration
git checkout -b task/MB-009-order-upload
```

---

## 📊 Commit History Örneği

İdeal bir git history şu şekilde görünmeli:

```
* [FEAT] Risk analiz motoru tamamlandı (TASK-BE-014)
* [TEST] Order upload endpoint testleri eklendi
* [FIX] Restaurant matching algoritması düzeltildi
* [REFACTOR] OCR parsing fonksiyonları ayrıldı
* [DOCS] API dokümantasyonu güncellendi
* [FEAT] Order upload endpoint eklendi (TASK-BE-011)
* [CHORE] Alembic migration sistemi kuruldu
* [FEAT] Database modelleri oluşturuldu
* [CHORE] Proje dokümantasyonu hazırlandı
* [INIT] İlk commit - proje başlatıldı
```

---

## 🚫 Commit Etmemesi Gerekenler

```bash
# .gitignore dosyasında olmalı:
- .env (gizli bilgiler)
- __pycache__/ (Python cache)
- node_modules/ (NPM paketleri)
- .vscode/ (IDE ayarları)
- *.log (log dosyaları)
- uploads/ (yüklenen görseller)
```

---

## 🆘 Sık Sorunlar ve Çözümleri

### Yanlış commit mesajı yazdım
```bash
# Son commit'i düzelt (henüz push edilmediyse)
git commit --amend -m "[FIX] Doğru mesaj"
```

### Yanlış dosya commit'ledim
```bash
# Son commit'ten dosya çıkar (henüz push edilmediyse)
git reset HEAD~1
git add <doğru_dosyalar>
git commit -m "[FEAT] Doğru mesaj"
```

### Commit'i geri almak istiyorum
```bash
# Son commit'i geri al (değişiklikler working directory'de kalır)
git reset --soft HEAD~1

# Son commit'i tamamen sil (DİKKAT: Değişiklikler kaybolur!)
git reset --hard HEAD~1
```

---

## 📝 Checklist (Her Commit Öncesi)

- [ ] `git status` ile değişiklikleri kontrol ettim
- [ ] Sadece ilgili dosyalar stage'lendi
- [ ] `.env` veya şifre gibi hassas bilgiler yok
- [ ] Commit mesajı kategori ile başlıyor (`[FEAT]`, `[FIX]`, vb.)
- [ ] Mesaj Türkçe ve anlaşılır
- [ ] 50 karakter limitini aşmıyor (başlık)
- [ ] Test edildi (mümkünse)

---

## 🎓 Örneklerle Pratik

### Senaryo 1: Login Endpoint Ekleme
```bash
# 1. Dosyaları kontrol et
git status

# 2. Stage'le
git add backend/app/api/auth.py backend/tests/test_auth.py

# 3. Commit
git commit -m "[FEAT] Kullanıcı login endpoint'i eklendi (TASK-BE-006)

- POST /v1/auth/login endpoint oluşturuldu
- JWT token dönüyor
- Login attempt sayacı eklendi
- Unit testler yazıldı
"

# 4. Push
git push
```

### Senaryo 2: Bug Düzeltme
```bash
git add backend/app/services/ocr_service.py
git commit -m "[FIX] OCR Türkçe karakter hatası giderildi

Sorun: EasyOCR 'Ş' karakterini yanlış okuyordu
Çözüm: UTF-8 encoding zorlaması eklendi
"
git push
```

### Senaryo 3: Dokümantasyon
```bash
git add Proje/docs/SPEC.md
git commit -m "[DOCS] API spesifikasyonu detaylandırıldı"
git push
```

---

## 📞 Yardım

Soru olursa:
- GitHub Issues kullan
- Team meeting'de sor
- Bu dökümanı güncelle (pull request ile)

---

**Son Güncelleme:** 21 Ocak 2026  
**Hazırlayan:** Mehmet Emre Kayacan & Mehmet Kurt  
**Durum:** ✅ Aktif Kullanımda

---

_"İyi commit mesajları, gelecekteki biz için en güzel hediyedir."_ 💝
