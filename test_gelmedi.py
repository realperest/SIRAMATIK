
import sys
import os

# Mevcut dizini path'e ekle
sys.path.append(os.getcwd())

from backend.database import Database

try:
    print("Veritabanına bağlanılıyor...")
    db = Database()
    print("Bağlantı başarılı.")
    
    # Test için bir sıra bul veya oluştur
    # Önce bekleyen bir sıra var mı bakalım
    sira = db.execute_query("SELECT id FROM siramatik.siralar LIMIT 1")
    
    if not sira:
        print("Test için sıra bulunamadı.")
    else:
        sira_id = sira[0]['id']
        print(f"Test edilecek sıra ID: {sira_id}")
        
        try:
            # Gelmedi olarak işaretlemeyi dene (SQL sorgusunu doğrudan çalıştırarak hatayı gör)
            print("Sorgu çalıştırılıyor...")
            db.execute_query("""
                UPDATE siramatik.siralar 
                SET durum = 'skipped', tamamlanma = NOW()
                WHERE id = :sira_id
                RETURNING *
            """, {"sira_id": sira_id})
            print("BAŞARILI: Sorgu hatasız çalıştı.")
            
            # Değişikliği geri al (Opsiyonel, test verisi olduğu için çok önemli değil)
            # db.execute_query("UPDATE siramatik.siralar SET durum = 'waiting' WHERE id = :sira_id", {"sira_id": sira_id})
            
        except Exception as e:
            print(f"HATA DETAYI: {e}")

except Exception as e:
    print(f"GENEL HATA: {e}")
