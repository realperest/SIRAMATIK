@echo off
echo ============================================
echo SIRAMATIK BASLATILIYOR...
echo ============================================

echo.
echo [1/2] Backend baslatiliyor (Port 8000)...
start "Siramatik Backend" cmd /k "cd backend && python main.py"

echo.
echo [2/2] Frontend baslatiliyor (Port 3000)...
start "Siramatik Frontend" cmd /k "cd frontend && python -m http.server 3000 --bind 0.0.0.0"

echo.
echo [3/3] Tarayici aciliyor...
timeout /t 3 /nobreak >nul
start http://localhost:3000/index.html

echo.
echo ============================================
echo SISTEM HAZIR!
echo ============================================
echo.
echo Giris Sayfasi: http://localhost:3000/index.html
echo.
echo Diger Sayfalar:
echo - Kiosk Ekrani:  http://localhost:3000/kiosk.html
echo - TV Ekrani:     http://localhost:3000/tv.html
echo.
echo Backend API Docs: http://localhost:8000/docs
echo.
pause
