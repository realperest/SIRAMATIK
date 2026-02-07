
import sys
import os

# Backend dizinini path'e ekle
sys.path.append(os.path.join(os.getcwd(), "backend"))

from database import db

def add_servis_column():
    print("Veritabanı güncelleniyor: kullanicilar tablosuna servis_id ekleniyor...")
    try:
        # 1. Kolonu ekle
        db.execute_query("""
            ALTER TABLE siramatik.kullanicilar 
            ADD COLUMN IF NOT EXISTS servis_id INTEGER REFERENCES siramatik.servisler(id) ON DELETE SET NULL;
        """)
        print("✅ Colum servis_id added successfully.")
        
    except Exception as e:
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    add_servis_column()
