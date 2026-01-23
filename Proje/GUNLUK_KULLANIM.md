# 🚀 GIDA NOBETI - GUNLUK KULLANIM REHBERI

## 📌 PC'yi Actiginda Yapilacaklar

### ADIM 1: Docker Desktop'i Ac
```
1. Windows tusuna bas
2. "Docker Desktop" yaz
3. Ac ve bekle (simge yesil olana kadar - 10 saniye)
```

**Kontrol:** Taskbar'da Docker ikonu yesil ✅

---

### ADIM 2: VS Code'u Ac
```
1. Windows tusuna bas
2. "Visual Studio Code" yaz
3. Ac
4. File -> Open Folder
5. C:\Users\emrem\Desktop\GidaNobeti\Proje sec
```

---

### ADIM 3: VS Code'da Terminal Ac
```
Ctrl + ` (Ters tirnak - ESC tusunun altinda)
```

Sag ust kosede + butonuna tikla -> **3 terminal ac**:
- Terminal 1: Docker
- Terminal 2: Backend
- Terminal 3: Admin Panel

---

### ADIM 4: Servisleri Baslat (Sirasıyla)

#### Terminal 1 - Docker Servisleri:
```powershell
docker-compose up -d
```
**Bekle:** "✔ Container gidanobeti_db Healthy" mesajini gor ✅

---

#### Terminal 2 - Backend API:
```powershell
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
**Bekle:** "🚀 Gıda Nöbeti API v1.0.0 started" mesajini gor ✅

**Test:** http://localhost:8000/docs adresini ac

---

#### Terminal 3 - Admin Panel:
```powershell
cd admin-panel
npm run dev
```
**Bekle:** "✓ Ready in 2.5s" mesajini gor ✅

**Test:** http://localhost:3000 adresini ac

---

### ADIM 5: Mobile (Opsiyonel - Gerekirse Ac)
**Yeni terminal ac (+ butonuna tikla):**

**Web Server Mode (Firefox, Chrome, vb. - ONERILIR):**
```powershell
cd mobile
flutter run -d web-server --web-port 3001
```
**Tarayicida ac:** http://localhost:3001

**Veya Edge/Chrome ile direkt:**
```powershell
cd mobile
flutter run
```
**Cihaz sec:** `2` yaz (Edge tarayici)

> **Not:** Web-server mode daha stabil, herhangi bir tarayicida acabilirsin.

---

### ✅ Sistem Hazir Kontrolu

**Tarayicida Ac:**
- ✅ Backend API: http://localhost:8000/docs
- ✅ Admin Panel: http://localhost:3000
- ✅ Mobile: http://localhost:3001 (Mobile web-server mode)

**Hepsi Acildiysa:** Kodlamaya baslayabilirsin! 🎉

---

## 💻 Kodlama Sirasinda

### Hot Reload (Otomatik Guncelleme)
- **Backend:** Kod degistir -> Kaydet -> Otomatik yenilenir ✅
- **Admin Panel:** Kod degistir -> Kaydet -> Tarayici otomatik yenilenir ✅
- **Mobile:** Kod degistir -> Kaydet -> Terminal'de `r` tusuna bas (veya tarayiciyi yenile F5) 🔄

### Terminal'leri Izle
- **Terminal 1 (Docker):** Mesaj vermez, arka planda calisir
- **Terminal 2 (Backend):** API isteklerini gosterir (POST /v1/auth/register, vb.)
- **Terminal 3 (Admin):** Next.js build log'lari
- **Terminal 4 (Mobile):** 
  - **Web-server mode:** Sadece hot reload komutlari gosterir
  - **Log'lar icin:** F12 (Developer Console) ac -> Console tab'i
  - **Edge/Chrome direkt mode:** Terminal'de BLoC log'lari gosterir

### Yeni Terminal Acma
```
Ctrl + Shift + ` (Yeni terminal)
Veya sag ustteki + butonuna tikla
```

---

## 🛑 Is Bittiginde (Kapanmadan Once)

### Terminal'lerde Durdurma (Sirasıyla)

**1. Mobile varsa:** `q` tusuna bas (terminal 4)

**2. Admin Panel:** `Ctrl + C` (terminal 3)

**3. Backend:** `Ctrl + C` (terminal 2)

**4. Docker (Opsiyonel):** 
```powershell
docker-compose down
```
Veya acik birak (problem olmaz)

**5. VS Code'u Kapat**

---

## ⚡ Hizli Komutlar

### Sadece Backend Yeniden Baslat
```powershell
# Terminal 2'de Ctrl+C ile durdur, sonra:
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Sadece Admin Panel Yeniden Baslat
```powershell
# Terminal 3'te Ctrl+C ile durdur, sonra:
cd admin-panel
npm run dev
```

### Docker'i Yeniden Baslat
```powershell
# Terminal 1'de:
docker-compose restart
```

### Docker Loglarini Gor
```powershell
docker logs gidanobeti_api --tail 50
docker logs gidanobeti_db --tail 50
```

---

## 🧪 API Test (Swagger UI)

### Backend API Test Adresi
```
http://localhost:8000/docs
```

### Kayit Endpoint Test (POST /v1/auth/register)
```json
{
  "tckn": "11111111110",
  "password": "Test1234",
  "full_name": "Test Kullanici",
  "email": "test@test.com",
  "phone": "05551234567",
  "dorm_id": "00000000-0000-0000-0000-000000000000",
  "room_number": "101"
}
```

### Login Endpoint Test (POST /v1/auth/login)
```json
{
  "tckn": "11111111110",
  "password": "Test1234"
}
```

**Basarili Test Ciktisi:**
- Status: 201 Created (register) veya 200 OK (login)
- Response: `access_token`, `token_type`, `user` bilgileri

---

## ❓ Sorun Cozumleri

### Docker Baslamiyor
```
Cozum: Docker Desktop'i kapat -> Tekrar ac -> Bekle (yesil tik)
```

### Backend "ModuleNotFoundError" Hatasi
```powershell
cd backend
pip install -r requirements.txt
```

### Admin Panel "npm ERR!" Hatasi
```powershell
cd admin-panel
npm install
```

### Mobile "packages get failed" Hatasi
```powershell
cd mobile
flutter pub get
```

### Port Cakismasi (8000 veya 3000 dolu)
```powershell
# Port 8000'i kontrol et
netstat -ano | findstr :8000

# Processi bul ve oldur:
Stop-Process -Id <PID> -Force

# Veya farkli port kullan:
uvicorn app.main:app --reload --port 8080
```

### Database Baglanti Hatasi
```powershell
# Docker DB'nin calistigini kontrol et:
docker ps

# Healthcheck bekle:
docker ps | findstr healthy

# Yeniden baslat:
docker-compose restart db
```

---

## 📁 Proje Yapisi Hatirlama

```
Proje/
├── backend/          # Python FastAPI (Terminal 2)
├── admin-panel/      # Next.js React (Terminal 3)
├── mobile/           # Flutter (Terminal 4)
├── docs/             # Dokumanlar
│   └── TASKS.md      # Gorev listesi
├── docker-compose.yml # Docker ayarlari (Terminal 1)
└── GUNLUK_KULLANIM.md # ⭐ BU DOSYA
```

---

## 🎯 Gunluk Checklist

**Sabah (PC Actiktan Sonra):**
- [ ] Docker Desktop ac (yesil tik bekle)
- [ ] VS Code ac (Proje klasorunu ac)
- [ ] Ctrl + ` (3 terminal ac)
- [ ] Terminal 1: `docker-compose up -d`
- [ ] Terminal 2: `cd backend` -> `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- [ ] Terminal 3: `cd admin-panel` -> `npm run dev`
- [ ] http://localhost:8000/docs ac (Backend test)
- [ ] http://localhost:3000 ac (Admin test)

**Aksam (Is Bitince):**
- [ ] Terminal 4 (Mobile): `q` tusuna bas
- [ ] Terminal 3 (Admin): Ctrl + C
- [ ] Terminal 2 (Backend): Ctrl + C
- [ ] Terminal 1 (Docker): `docker-compose down` (opsiyonel)
- [ ] VS Code'u kapat

**Hizli Baslangic (Sadece Backend Test Icin):**
- [ ] Docker Desktop ac
- [ ] VS Code ac
- [ ] Terminal 1: `docker-compose up -d`
- [ ] Terminal 2: `cd backend` -> `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- [ ] http://localhost:8000/docs ac

---

## 📞 Yardim

- **TASKS.md:** Gorev listesi ve durum takibi
- **README_TR.md:** Detayli kurulum ve kullanim
- **SPEC.md:** Teknik ozellikler

---

**Son Guncelleme:** 23 Ocak 2026
