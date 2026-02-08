#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "============================================"
echo "SIRAMATIK BASLATILIYOR (macOS)..."
echo "============================================"

echo ""
echo "[1/2] Backend baslatiliyor (Port 8000)..."
osascript -e "tell application \"Terminal\" to do script \"cd '$DIR/backend' && python3 main.py\""

echo ""
echo "[2/2] Frontend baslatiliyor (Port 3000)..."
osascript -e "tell application \"Terminal\" to do script \"cd '$DIR/frontend' && python3 -m http.server 3000\""

echo ""
echo "[3/3] Tarayici aciliyor..."
sleep 3
open http://localhost:3000/index.html

echo ""
echo "============================================"
echo "SISTEM HAZIR!"
echo "============================================"
echo ""
echo "Giris Sayfasi: http://localhost:3000/index.html"
echo ""
echo "Diger Sayfalar:"
echo "- Kiosk Ekrani:  http://localhost:3000/kiosk.html"
echo "- TV Ekrani:     http://localhost:3000/tv.html"
echo ""
echo "Backend API Docs: http://localhost:8000/docs"
echo ""
