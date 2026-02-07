
import sys
import os

# Backend dizinini path'e ekle
sys.path.append(os.path.join(os.getcwd(), "backend"))

from database import db

def check_servis_type():
    print("Veritabanı servisler tablosu kontrol ediliyor...")
    try:
        res = db.execute_query("SELECT id FROM siramatik.servisler LIMIT 1")
        if res:
            first_row = res[0]
            val = first_row.get('id')
            if val is None:
                # Belki 'ID' falan diye büyük harftir?
                val = list(first_row.values())[0]
                
            print(f"ID Tipi: {type(val)}")
            print(f"ID Değeri: {val}")
        else:
            print("Servis bulunamadı!")
            
    except Exception as e:
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    check_servis_type()
