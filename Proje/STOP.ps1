# GIDA NOBETI - TUM UYGULAMALARI DURDURMA

Write-Host "Gida Nobeti Uygulamalari Durduruluyor..." -ForegroundColor Red
Write-Host ""

$ProjectRoot = $PSScriptRoot
Set-Location $ProjectRoot

# 1. DOCKER SERVICES
Write-Host "1/4 Docker Servisleri Durduruluyor..." -ForegroundColor Yellow
docker-compose down 2>&1 | Out-Null
Write-Host "   Docker durduruldu" -ForegroundColor Green
Start-Sleep -Milliseconds 500

# 2. BACKEND (PORT 8000)
Write-Host "2/4 Backend (Port 8000) Kapatiliyor..." -ForegroundColor Yellow
$backendProcesses = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
if ($backendProcesses) {
    foreach ($pid in $backendProcesses) {
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    }
    Write-Host "   Backend kapatildi" -ForegroundColor Green
} else {
    Write-Host "   Backend zaten kapali" -ForegroundColor Cyan
}
Start-Sleep -Milliseconds 500

# 3. ADMIN PANEL (PORT 3000)
Write-Host "3/4 Admin Panel (Port 3000) Kapatiliyor..." -ForegroundColor Yellow
$adminProcesses = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
if ($adminProcesses) {
    foreach ($pid in $adminProcesses) {
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    }
    Write-Host "   Admin Panel kapatildi" -ForegroundColor Green
} else {
    Write-Host "   Admin Panel zaten kapali" -ForegroundColor Cyan
}
Start-Sleep -Milliseconds 500

# 4. TUM ILGILI PROCESSLERI KAPAT (Fazladan Temizlik)
Write-Host "4/4 Tum Python/Node/Flutter Processleri Temizleniyor..." -ForegroundColor Yellow
$cleaned = 0

# Python
Get-Process python* -ErrorAction SilentlyContinue | ForEach-Object {
    Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    $cleaned++
}

# Node
Get-Process node* -ErrorAction SilentlyContinue | ForEach-Object {
    Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    $cleaned++
}

# Flutter/Dart
Get-Process flutter*, dart* -ErrorAction SilentlyContinue | ForEach-Object {
    Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    $cleaned++
}

if ($cleaned -gt 0) {
    Write-Host "   $cleaned process temizlendi" -ForegroundColor Green
} else {
    Write-Host "   Temizlenecek process bulunamadi" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "TUM UYGULAMALAR DURDURULDU!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "NOT: Acik terminal pencerelerini manuel kapatabilirsiniz (X tusuna basin)." -ForegroundColor Yellow
Write-Host ""

Start-Sleep -Seconds 2
