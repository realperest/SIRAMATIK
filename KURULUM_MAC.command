#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "============================================"
echo "SIRAMATIK MAC KURULUMU BASLATILIYOR..."
echo "============================================"
echo ""

# 1. Portaudio kontrol (PyAudio icin gerekli)
echo "[1/3] Portaudio kontrol ediliyor..."
if ! brew list portaudio &>/dev/null; then
    echo "Portaudio bulunamadi, Homebrew ile yukleniyor..."
    if command -v brew &>/dev/null; then
        brew install portaudio
    else
        echo "HATA: Homebrew yuklu degil! Lutfen once Homebrew yukleyin:"
        echo "/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
else
    echo "Portaudio zaten yuklu."
fi

# 2. Gereksinim listesi hazirlama
echo ""
echo "[2/3] Gereksinim listesi hazirlaniyor..."
python3 prepare_mac_requirements.py

# 3. Kutuphaneleri yukleme
echo ""
echo "[3/3] Python kutuphaneleri yukleniyor..."
python3 -m pip install -r backend/requirements_mac.txt

echo ""
echo "============================================"
echo "KURULUM TAMAMLANDI!"
echo "Artik 'BASLAT.command' dosyasi ile sistemi baslatabilirsiniz."
echo "============================================"
echo "" 
read -p "Cikmak icin bir tusa basin..."
