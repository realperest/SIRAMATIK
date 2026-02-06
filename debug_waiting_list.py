
import sys
import os
import requests
import json
from datetime import datetime

# Backend dizinini path'e ekle
sys.path.append(os.path.join(os.getcwd(), "backend"))

from database import db

# Firma ID'miz (veritabanından alabiliriz veya sabit)
FIRMA_ID = '11111111-1111-1111-1111-111111111111'

def test_db_direct():
    print(f"\n--- VERİTABANI SORGUSU ({datetime.now()}) ---")
    try:
        siralar = db.get_tum_bekleyen_siralar(FIRMA_ID)
        print(f"Veritabanından dönen satır sayısı: {len(siralar)}")
        if len(siralar) > 0:
            orn = siralar[0]
            print(f"Örnek satır keys: {list(orn.keys())}")
            print(f"Örnek satır: {orn}")
            
            if 'numara' not in orn:
                print("⚠ UYARI: 'numara' alanı yok!")
            else:
                print(f"Numara: {orn['numara']}")
    except Exception as e:
        print(f"HATA: {e}")

if __name__ == "__main__":
    test_db_direct()
