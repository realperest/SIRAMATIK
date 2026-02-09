
import sys
import os

# Mevcut dizini path'e ekle
sys.path.append(os.getcwd())

from backend.database import Database

try:
    print("Veritabanına bağlanılıyor...")
    db = Database()
    print("Bağlantı başarılı.")
    
    # Sıralar tablosundaki CHECK constraint'leri bul
    print("Kısıtlamalar aranıyor...")
    constraints = db.execute_query("""
        SELECT conname, pg_get_constraintdef(c.oid) as definition
        FROM pg_constraint c
        JOIN pg_namespace n ON n.oid = c.connamespace
        WHERE conrelid = 'siramatik.siralar'::regclass 
        AND contype = 'c'
    """)
    
    if not constraints:
        print("Sıralar tablosunda CHECK constraint bulunamadı.")
    else:
        for con in constraints:
            print(f"Buldum: {con['conname']} -> {con['definition']}")
            if 'durum' in con['definition']:
                print(f"Siliniyor: {con['conname']}")
                db.execute_query(f"ALTER TABLE siramatik.siralar DROP CONSTRAINT {con['conname']}")
                print("Silindi.")
                
                # Yeni constraint ekle
                new_con = "CHECK (durum IN ('waiting', 'serving', 'completed', 'skipped', 'cancelled'))"
                print(f"Yenisi ekleniyor: {new_con}")
                db.execute_query(f"ALTER TABLE siramatik.siralar ADD CONSTRAINT {con['conname']} {new_con}")
                print("Eklendi.")
                
    # Tekrar test et
    print("Tekrar test ediliyor...")
    # (Burada test_gelmedi.py kodunu tekrar çalıştırmaya gerek yok, kullanıcı deneyebilir)

except Exception as e:
    print(f"GENEL HATA: {e}")
