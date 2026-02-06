
import psycopg2
import uuid
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="backend/.env")

# Supabase Bağlantı Ayarları
DB_URL = "postgresql://postgres.wyursjdrnnjabpfeucyi:qk4SEnyhu3NUk2@aws-1-eu-central-1.pooler.supabase.com:6543/postgres"

FIRMA_ID = '11111111-1111-1111-1111-111111111111'

def seed_queues():
    try:
        conn = psycopg2.connect(DB_URL)
        conn.autocommit = True
        cur = conn.cursor()
        
        # Schema ayarla
        cur.execute("SET search_path TO siramatik, public;")

        
        print("Mevcut servisler kontrol ediliyor...")
        cur.execute("SELECT id, ad, kod FROM servisler WHERE firma_id = %s", (FIRMA_ID,))
        servisler = cur.fetchall()
        
        if not servisler:
            print("HATA: Hiç servis bulunamadı! Lütfen önce servisleri oluşturun.")
            return

        print(f"{len(servisler)} servis bulundu. Kuyruklar oluşturuluyor...")
        
        for servis_id, ad, kod in servisler:
            # Kuyruk var mı kontrol et
            cur.execute("SELECT id FROM kuyruklar WHERE servis_id = %s", (servis_id,))
            mevcut = cur.fetchone()
            
            if mevcut:
                print(f" - {ad} için kuyruk zaten var.")
            else:
                kuyruk_id = str(uuid.uuid4())
                cur.execute("""
                    INSERT INTO kuyruklar (id, servis_id, ad, kod, aktif, oncelik)
                    VALUES (%s, %s, %s, %s, true, 0)
                """, (kuyruk_id, servis_id, f"{ad} Kuyruğu", f"Q-{kod}"))
                print(f" + {ad} için kuyruk oluşturuldu: {kuyruk_id}")
        
        print("İşlem tamamlandı!")
        
    except Exception as e:
        print(f"Bir hata oluştu: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    seed_queues()
