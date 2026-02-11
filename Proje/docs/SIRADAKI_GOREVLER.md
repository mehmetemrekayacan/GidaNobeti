# Sıradaki Geliştirme Görevleri

**Güncelleme:** Şubat 2026  
**Durum:** Demo UI tamamlandı, Orders API çalışıyor

---

## Tamamlananlar (Son Çalışma)

- ✅ Orders sayfası gerçek API bağlantısı (`GET /admin/orders`)
- ✅ Demo veri göstergesi (API hatasında)
- ✅ Dashboard periyot seçimi (7/30 gün)
- ✅ Restaurants sayfası API bağlantısı (zaten vardı)
- ✅ Incidents sayfası API bağlantısı (zaten vardı)
- ✅ `RestaurantListItem` şemasına `risk_reason` alanı eklendi
- ✅ Admin panel Restaurants sayfası risk nedeni gösteriyor
- ✅ Orders sayfasında backend destekli sayfalama + \"Daha fazla yükle\" butonu

---

## Öncelikli Sıradaki Görevler

### 1. Admin Panel İyileştirmeleri (Kolay – ~2–4 saat)

| Görev | Açıklama | Süre |
|-------|----------|------|
| **Öğrenci listesi sayfası** | Admin panelde \"Students\" menüsü için `GET /admin/users` veya benzeri | ~2 saat |

### 2. Backend Geliştirmeleri (Orta – ~4–8 saat)

| Görev | Açıklama | Süre |
|-------|----------|------|
| **Auth required (production)** | Dashboard, Orders, Restaurants, Incidents endpoint'lerine `require_admin` ekle | ~1 saat |
| **Redis cache** | Dashboard stats için 10 dk cache (TASKS'ta var) | ~2 saat |
| **Audit log** | Risk güncelleme, vaka durum değişikliği için audit kaydı | ~3 saat |

### 3. Mobile Uygulama (Büyük – PLAN.md Faz 2)

| Görev | Açıklama | Süre |
|-------|----------|------|
| **Login/Register** | Flutter auth ekranları, API entegrasyonu | ~2 gün |
| **Home (Risk Panosu)** | Riskli restoranlar listesi, `GET /restaurants/risky` | ~3 gün |
| **Order Upload** | Kamera/galeri, `POST /orders/upload` | ~3 gün |
| **Order History** | `GET /orders/my-history` | ~2 gün |

### 4. DevOps & Deployment (İleride)

| Görev | Açıklama |
|-------|----------|
| **Production Server** | DigitalOcean/AWS droplet, Docker |
| **Domain & SSL** | api.gidanobeti.gov.tr, Let's Encrypt |
| **CI/CD** | GitHub Actions ile otomatik deploy |

---

## Hemen Başlanabilecekler (Bugün)

1. **Auth guard** – Admin endpoint'lerine `require_admin` (production için gözden geçirme) (~30 dk)
2. **Öğrenci listesi sayfası** – Admin panelde öğrencileri listeleyen sayfa (~2 saat)
3. **Redis cache (Dashboard)** – Stats endpoint'i için 10 dk cache (~2 saat)

---

## Referanslar

- `docs/TASKS.md` – Detaylı görev listesi
- `docs/PLAN.md` – Sprint planlaması
- `docs/SPEC.md` – API şeması
