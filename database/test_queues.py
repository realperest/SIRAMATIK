
import sys
import os
import json
from datetime import datetime

# Backend dizinini path'e ekle
sys.path.append(os.path.join(os.getcwd(), "backend"))

from database import db

FIRMA_ID = '11111111-1111-1111-1111-111111111111'

def test_kuyruklar():
    print(f"[{datetime.now()}] Kuyruklar test ediliyor... (Firma ID: {FIRMA_ID})")
    
    try:
        kuyruklar = db.get_kuyruklar_by_firma(FIRMA_ID)
        print(f"Toplam Kuyruk Sayısı: {len(kuyruklar)}")
        
        for k in kuyruklar:
            print(f"- ID: {k['id']}")
            print(f"  Ad: {k['ad']}")
            print(f"  Kod: {k['kod']}")
            print(f"  Servis ID: {k['servis_id']}")
            print("-" * 30)
            
    except Exception as e:
        print(f"HATA: {e}")

if __name__ == "__main__":
    test_kuyruklar()
