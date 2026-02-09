# 🍽️ GIDA NÖBETİ | Yurt Gıda Güvenliği Platformu

**KYK yurtlarında harici gıda siparişlerinin dijital takibi ve güvenlik analizi sistemi**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Flutter](https://img.shields.io/badge/Flutter-3.16+-blue.svg)](https://flutter.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)

---

## 📋 Proje Hakkında

**Gıda Nöbeti**, Gençlik ve Spor Bakanlığı yurtlarında barınan öğrencilerin dışarıdan temin ettikleri gıdaların dijital olarak kayıt altına alınmasını ve olası gıda zehirlenmesi vakalarında kaynağın anında tespit edilmesini sağlayan bir mobil ve web tabanlı güvenlik platformudur.

### 🎯 Temel Özellikler

- 📱 **Mobil Uygulama** (Öğrenci): Fiş/ekran görüntüsü ile sipariş kaydı
- 🤖 **OCR Teknolojisi**: Otomatik metin tanıma (Türkçe desteği)
- 🚨 **Risk Analiz Motoru**: Otomatik restoran risk tespiti
- 🔴 **Kırmızı Alarm**: Riskli restoranlardan gelen siparişleri engelleme
- 💻 **Yönetici Paneli**: Dashboard ve raporlama
- 🔒 **KVKK Uyumlu**: Görüntüler saklanmaz, sadece metin verisi

---

## 🏗️ Mimari

```
┌─────────────────────────────────────────────┐
│         CLIENT LAYER                         │
│  Mobile (Flutter) + Admin Panel (React)     │
└──────────────────┬──────────────────────────┘
                   │ HTTPS/TLS
┌──────────────────▼──────────────────────────┐
│        APPLICATION LAYER                     │
│  FastAPI + OCR Service + Risk Engine        │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│         DATA LAYER                           │
│  PostgreSQL 16 + Redis Cache                │
└─────────────────────────────────────────────┘
```

**Detaylı mimari:** [Proje/docs/SPEC.md](Proje/docs/SPEC.md)

---

## 🚀 Hızlı Başlangıç

### Gereksinimler

- **Backend**: Python 3.11+, Docker, PostgreSQL 16
- **Mobile**: Flutter 3.16+, Android Studio / Xcode
- **Admin**: Node.js 18+, npm/yarn

### Backend Kurulumu

```bash
# Repository'yi klonla
git clone https://github.com/mehmetemrekayacan/GidaNobeti.git
cd GidaNobeti

# Docker ile başlat
docker-compose up -d

# API dokümantasyonu
open http://localhost:8000/docs
```

### Mobile Kurulumu

```bash
cd mobile
flutter pub get
flutter run
```

**Detaylı kurulum:** [INSTALLATION.md](INSTALLATION.md) _(yakında)_

---

## 📚 Dokümantasyon

| Dosya | İçerik |
|-------|--------|
| [ARCHITECTURE.md](Proje/docs/ARCHITECTURE.md) | Mimari özeti, klasör yapısı, veritabanı şeması |
| [SPEC.md](Proje/docs/SPEC.md) | Teknik spesifikasyonlar, API dok., veritabanı şeması |
| [PLAN.md](Proje/docs/PLAN.md) | Geliştirme planı, roadmap, sprint detayları |
| [TASKS.md](Proje/docs/TASKS.md) | Detaylı görev listesi (60+ task) |
| [COMMIT_STANDARDS.md](COMMIT_STANDARDS.md) | Git commit standartları |

---

## 🛠️ Teknoloji Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL 16
- **Cache**: Redis
- **OCR**: EasyOCR / PaddleOCR
- **Auth**: JWT (python-jose)

### Mobile
- **Framework**: Flutter/Dart
- **State Management**: BLoC
- **Network**: Dio + Retrofit
- **Storage**: flutter_secure_storage

### DevOps
- **Containerization**: Docker + Docker Compose
- **Web Server**: Nginx
- **Monitoring**: Sentry
- **CI/CD**: GitHub Actions

---

## 📊 Proje Durumu

**Versiyon:** 1.0.0 (MVP)  
**Durum:** 🚧 Geliştirme Aşamasında  
**Hedef Pilot Teslim:** 15 Mart 2026  
**Tam Deployment:** 1 Haziran 2026

### Tamamlanan İşler
- [x] Proje dokümantasyonu (SPEC, PLAN, TASKS)
- [x] Git repository kurulumu
- [ ] Backend altyapı (Docker + FastAPI)
- [ ] OCR servis entegrasyonu
- [ ] Mobile app (Flutter)
- [ ] Admin panel (React/Next.js)

**Detaylı ilerleme:** [PLAN.md](Proje/docs/PLAN.md)

---

## 🤝 Katkıda Bulunma

Projeye katkıda bulunmak için:

1. Bu repository'yi fork edin
2. Feature branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Değişikliklerinizi commit edin ([COMMIT_STANDARDS.md](COMMIT_STANDARDS.md)'ye uygun)
4. Branch'inizi push edin (`git push origin feature/yeni-ozellik`)
5. Pull Request açın

**Commit Formatı:**
```bash
[KATEGORİ] Kısa açıklama

Detaylı açıklama:
- Ne değişti?
- Neden değişti?
```

---

## 👥 Takım

- **Mehmet Emre Kayacan** - Backend Lead, DevOps
- **Mehmet Kurt** - Mobile Lead, OCR Integration

---

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

---

## 📞 İletişim

- **Email**: [proje iletişim emaili]
- **GitHub Issues**: [Issue oluştur](https://github.com/mehmetemrekayacan/GidaNobeti/issues)

---

## 🙏 Teşekkürler

- Gençlik ve Spor Bakanlığı - Proje desteği
- Isparta Erkek KYK Yurdu - Pilot uygulama
- EasyOCR - OCR kütüphanesi

---

## 📈 Roadmap

- ✅ **Faz 1** (Ocak 2026): Proje planlaması ve dokümantasyon
- 🚧 **Faz 2** (Şubat 2026): Backend + Mobile MVP
- ⏳ **Faz 3** (Mart 2026): Pilot uygulama (Isparta)
- ⏳ **Faz 4** (Nisan-Haziran 2026): 81 il deployment

**Detaylı roadmap:** [PLAN.md#roadmap](Proje/docs/PLAN.md)

---

## 🔒 Güvenlik

Bu proje KVKK (Kişisel Verilerin Korunması Kanunu) uyumludur:
- ✅ Fiş/ekran görüntüleri sunucuda saklanmaz (RAM-only processing)
- ✅ TCKN şifrelenerek saklanır
- ✅ JWT ile güvenli authentication
- ✅ HTTPS/TLS 1.3 şifreleme

Güvenlik açığı bildirimi: [güvenlik email adresi]

---

**Son Güncelleme:** 21 Ocak 2026  
**Proje Başlangıç:** 21 Ocak 2026

---

_"Sağlıklı gıda, güvenli yarın."_ 🍽️✨
