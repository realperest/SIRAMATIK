
import sys
import os
import json
from datetime import datetime

# Backend dizinini path'e ekle
sys.path.append(os.path.join(os.getcwd(), "backend"))

from database import db

def check_last_rows():
    print(f"[{datetime.now()}] Son eklenen sıralar kontrol ediliyor...")
    
    # Son 10 sırayı getir (durum farketmeksizin)
    rows = db.execute_query("""
        SELECT numara, s.durum, s.olusturulma, k.ad as kuyruk_ad
        FROM siralar s
        JOIN kuyruklar k ON s.kuyruk_id = k.id
        ORDER BY s.olusturulma DESC
        LIMIT 10
    """)
    
    print("\nSON 10 SIRA KAYDI:")
    print("-" * 60)
    print(f"{'NUMARA':<10} {'DURUM':<15} {'OLUŞTURULMA':<25} {'KUYRUK'}")
    print("-" * 60)
    
    for r in rows:
        print(f"{r['numara']:<10} {r['durum']:<15} {str(r['olusturulma']):<25} {r['kuyruk_ad']}")
        
    print("-" * 60)

if __name__ == "__main__":
    check_last_rows()
