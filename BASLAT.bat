@echo off
echo ============================================
echo SIRAMATIK BASLATILIYOR...
echo ============================================

echo.
echo [1/2] Backend baslatiliyor (Port 8000)...
start "Siramatik Backend" cmd /k "cd backend && python main.py"

echo.
echo [2/2] Frontend baslatiliyor (Port 3000)...
start "Siramatik Frontend" cmd /k "cd frontend && python -m http.server 3000"

echo.
echo ============================================
echo SISTEM HAZIR!
echo ============================================
echo.
echo 1. Hizmet Veren Paneli: http://localhost:3000/personel.html
echo 2. Kiosk Ekrani:  http://localhost:3000/kiosk.html
echo 3. TV Ekrani:     http://localhost:3000/tv.html
echo.
echo Backend API Docs: http://localhost:8000/docs
echo.
pause
