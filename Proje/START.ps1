# GIDA NOBETI - TUM UYGULAMALARI BASLATMA

Write-Host "Gida Nobeti Uygulamalari Baslatiliyor..." -ForegroundColor Cyan
Write-Host ""

$ProjectRoot = $PSScriptRoot
Set-Location $ProjectRoot

# 1. DOCKER SERVICES
Write-Host "1/4 Docker Servisleri Baslatiliyor (PostgreSQL + Redis)..." -ForegroundColor Yellow
docker-compose up -d db redis

if ($LASTEXITCODE -eq 0) {
    Write-Host "   Docker servisleri baslatildi (PostgreSQL: 5432, Redis: 6379)" -ForegroundColor Green
} else {
    Write-Host "   Docker servisleri baslatilamadi! Docker Desktop acik mi?" -ForegroundColor Red
    Read-Host "Devam etmek icin Enter'a basin"
}

Start-Sleep -Seconds 3
Write-Host ""

# 2. BACKEND
Write-Host "2/4 Backend API Baslatiliyor (FastAPI - Port 8000)..." -ForegroundColor Yellow

Start-Process powershell -WorkingDirectory "$ProjectRoot\backend" -ArgumentList "-NoExit", "-Command", @"
Write-Host 'Backend Baslatiliyor...' -ForegroundColor Cyan
& '$ProjectRoot\..\.venv\Scripts\Activate.ps1'
Write-Host 'Dependencies kontrol ediliyor...' -ForegroundColor Yellow
pip install -r requirements.txt --quiet
Write-Host 'FastAPI baslatiliyor: http://localhost:8000' -ForegroundColor Green
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"@

Write-Host "   Backend terminal acildi (http://localhost:8000)" -ForegroundColor Green
Start-Sleep -Seconds 2
Write-Host ""

# 3. ADMIN PANEL
Write-Host "3/4 Admin Panel Baslatiliyor (Next.js - Port 3000)..." -ForegroundColor Yellow

Start-Process powershell -WorkingDirectory "$ProjectRoot\admin-panel" -ArgumentList "-NoExit", "-Command", @"
Write-Host 'Admin Panel Baslatiliyor...' -ForegroundColor Cyan
Write-Host 'Dependencies kontrol ediliyor...' -ForegroundColor Yellow
npm install
Write-Host 'Next.js baslatiliyor: http://localhost:3000' -ForegroundColor Green
npm run dev
"@

Write-Host "   Admin Panel terminal acildi (http://localhost:3000)" -ForegroundColor Green
Start-Sleep -Seconds 2
Write-Host ""

# 4. MOBILE APP
Write-Host "4/4 Mobile App Baslatiliyor (Flutter)..." -ForegroundColor Yellow
Write-Host "   Cihaz secimi yapilacak..." -ForegroundColor Cyan

Start-Process powershell -WorkingDirectory "$ProjectRoot\mobile" -ArgumentList "-NoExit", "-Command", @"
Write-Host 'Mobile App Baslatiliyor...' -ForegroundColor Cyan
Write-Host 'Dependencies kontrol ediliyor...' -ForegroundColor Yellow
flutter pub get
Write-Host 'Kullanilabilir cihazlar:' -ForegroundColor Green
flutter devices
Write-Host ''
Write-Host 'Flutter baslatiliyor (cihaz secimi yapacaksiniz)...' -ForegroundColor Green
Write-Host 'Edge (web) = 2, Android Emulator = secenekte gorunur' -ForegroundColor Yellow
flutter run
"@

Write-Host "   Mobile terminal acildi (cihaz secimi yapacaksiniz)" -ForegroundColor Green
Write-Host ""

# OZET
Start-Sleep -Seconds 1
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TUM UYGULAMALAR BASLATILDI!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "ERISIM ADRESLERI:" -ForegroundColor Yellow
Write-Host "   PostgreSQL:  localhost:5432 (User: gidanobeti)" -ForegroundColor White
Write-Host "   Redis:       localhost:6379" -ForegroundColor White
Write-Host "   Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs:    http://localhost:8000/docs" -ForegroundColor White
Write-Host "   Admin Panel: http://localhost:3000" -ForegroundColor White
Write-Host "   Mobile App:  (Cihaz secimi sonrasi)" -ForegroundColor White
Write-Host ""
Write-Host "YONETIM:" -ForegroundColor Yellow
Write-Host "   Tum servisleri durdurmak: docker-compose down" -ForegroundColor White
Write-Host "   Backend durdurmak: Backend terminalinde Ctrl+C" -ForegroundColor White
Write-Host "   Admin Panel durdurmak: Admin Panel terminalinde Ctrl+C" -ForegroundColor White
Write-Host "   Mobile durdurmak: Mobile terminalinde q tusuna basin" -ForegroundColor White
Write-Host ""
Write-Host "NOT: Backend ve Admin Panel otomatik reload destekler (kod degisikligi = aninda guncelleme)" -ForegroundColor Cyan
Write-Host ""

Set-Location $ProjectRoot
Write-Host "Iyi calismalar! Bu pencereyi kapatabilirsiniz." -ForegroundColor Green
Write-Host ""

Start-Sleep -Seconds 2
