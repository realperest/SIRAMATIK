
import sys
import os

# Mevcut dizini path'e ekle
sys.path.append(os.getcwd())

from backend.database import Database

try:
    print("Veritabanına bağlanılıyor...")
    db = Database()
    print("Bağlantı başarılı.")
    
    print("Tablo yapısı kontrol ediliyor...")
    try:
        # Sütunu eklemeyi dene
        db.execute_query("ALTER TABLE siramatik.siralar ADD COLUMN tamamlanma TIMESTAMP")
        print("BAŞARILI: 'tamamlanma' sütunu eklendi.")
    except Exception as e:
        err = str(e)
        if "duplicate" in err or "already exists" in err:
            print("BİLGİ: 'tamamlanma' sütunu zaten mevcut.")
        else:
            print(f"HATA: Sütun eklenirken hata oluştu: {err}")

except Exception as e:
    print(f"GENEL HATA: {e}")
