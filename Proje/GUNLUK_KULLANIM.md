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

### ADIM 3: Tum Uygulamalari Baslat (TEK KOMUT)
```
1. Proje klasorunde START.bat dosyasina cift tikla
   VEYA
2. VS Code'da Terminal ac (Ctrl + `)
3. Su komutu calistir:
```

```cmd
START.bat
```

**Ne Olacak:**
- 4 terminal penceresi acilacak
- Docker servisleri baslayacak (PostgreSQL + Redis)
- Backend baslayacak (http://localhost:8000)
- Admin Panel baslayacak (http://localhost:3000)
- Mobile baslayacak (cihaz secimi yapacaksin)

**Mobile Icin:** Terminal'de `2` yaz (Edge web tarayici)

---

### ADIM 4: Sistemin Calistigini Kontrol Et

**Tarayicida Ac:**
- Backend API: http://localhost:8000/docs
- Admin Panel: http://localhost:3000
- Mobile: Otomatik acilir (Edge'de)

**Hepsi Acildiysa:** ✅ Kodlamaya baslayabilirsin!

---

## 💻 Kodlama Sirasinda

### Hot Reload (Otomatik Guncelleme)
- **Backend:** Kod degistir -> Kaydet -> Otomatik yenilenir ✅
- **Admin Panel:** Kod degistir -> Kaydet -> Tarayici otomatik yenilenir ✅
- **Mobile:** Kod degistir -> Kaydet -> Terminal'de `r` tusuna bas 🔄

### Terminal'leri Izle
- Backend terminal: API isteklerini gosterir
- Admin terminal: Next.js build log'lari
- Mobile terminal: Flutter hot reload mesajlari

---

## 🛑 Is Bittiginde (Kapanmadan Once)

### ADIM 1: Tum Uygulamalari Durdur
```cmd
STOP.bat
```

**Veya Manuel:**
- Backend terminal: Ctrl + C
- Admin terminal: Ctrl + C
- Mobile terminal: q tusuna bas
- Docker: `docker-compose down` (opsiyonel - acik kalabilir)

---

## ⚡ Hizli Komutlar

### Sadece Backend Baslat
```powershell
cd backend
& ..\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

### Sadece Admin Panel Baslat
```powershell
cd admin-panel
npm run dev
```

### Sadece Mobile Baslat
```powershell
cd mobile
flutter run
```

### Docker'i Yeniden Baslat
```powershell
docker-compose restart
```

---

## ❓ Sorun Cozumleri

### Docker Baslamiyor
```
Cozum: Docker Desktop'i kapat -> Tekrar ac -> Bekle
```

### Backend Baslamiyor
```powershell
cd backend
& ..\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Admin Panel Baslamiyor
```powershell
cd admin-panel
npm install
```

### Mobile Baslamiyor
```powershell
cd mobile
flutter pub get
```

### Port Cakismasi (3000 veya 8000 dolu)
```powershell
# Port 8000'i kontrol et
netstat -ano | findstr :8000

# Eger baska bir program kullaniyorsa, o programi kapat
# Veya Backend'i farkli porttan baslat:
uvicorn app.main:app --reload --port 8080
```

---

## 📁 Proje Yapisi Hatirlama

```
Proje/
├── backend/          # Python FastAPI
├── admin-panel/      # Next.js React
├── mobile/           # Flutter
├── docs/             # Dokumanlar
│   └── TASKS.md      # Gorev listesi
├── START.bat         # ⭐ TUM UYGULAMALARI BASLAT
├── STOP.bat          # 🛑 TUM UYGULAMALARI DURDUR
└── docker-compose.yml # Docker ayarlari
```

---

## 🎯 Gunluk Checklist

**Sabah (PC Actiktan Sonra):**
- [ ] Docker Desktop ac (yesil tik bekle)
- [ ] VS Code ac
- [ ] START.bat calistir
- [ ] http://localhost:8000/docs ac (Backend test)
- [ ] http://localhost:3000 ac (Admin test)
- [ ] Mobile cihaz sec (2 = Edge)

**Aksam (Is Bitince):**
- [ ] STOP.bat calistir
- [ ] Tum terminal'leri kapat
- [ ] VS Code'u kapat
- [ ] Docker Desktop acik kalabilir (opsiyonel)

---

## 📞 Yardim

- **TASKS.md:** Gorev listesi ve durum takibi
- **README_TR.md:** Detayli kurulum ve kullanim
- **SPEC.md:** Teknik ozellikler

---

**Son Guncelleme:** 23 Ocak 2026
