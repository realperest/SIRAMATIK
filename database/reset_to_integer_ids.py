
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="backend/.env")

# Supabase Bağlantı Ayarları
DB_URL = "postgresql://postgres.wyursjdrnnjabpfeucyi:qk4SEnyhu3NUk2@aws-1-eu-central-1.pooler.supabase.com:6543/postgres"

def reset_database():
    try:
        conn = psycopg2.connect(DB_URL)
        conn.autocommit = True
        cur = conn.cursor()
        
        # Schema ayarla
        cur.execute("SET search_path TO siramatik, public;")
        
        print("Tablolar siliniyor...")
        # Bağımlılık sırasına göre sil
        cur.execute("""
            DROP TABLE IF EXISTS cihaz_olaylari CASCADE;
            DROP TABLE IF EXISTS cihazlar CASCADE;
            DROP TABLE IF EXISTS siralar CASCADE;
            DROP TABLE IF EXISTS kullanicilar CASCADE;
            DROP TABLE IF EXISTS kuyruklar CASCADE;
            DROP TABLE IF EXISTS servisler CASCADE;
            DROP TABLE IF EXISTS firmalar CASCADE;
            DROP TABLE IF EXISTS sistem_ayarlari CASCADE;
        """)
        
        print("Yeni şema uygulanıyor (02_tables_public.sql)...")
        with open("database/02_tables_public.sql", "r", encoding="utf-8") as f:
            sql = f.read()
            cur.execute(sql)
            
        print("Fonksiyonlar oluşturuluyor (04_functions.sql)...")
        with open("database/04_functions.sql", "r", encoding="utf-8") as f:
            sql = f.read()
            cur.execute(sql)
            
        print("Seed data ekleniyor...")
        # 1 Firma, 3 Servis, 3 Kuyruk, 1 Kullanıcı (HASH Şifreyle: admin123)
        cur.execute("""
            INSERT INTO firmalar (id, ad) VALUES (1, 'DEMO HASTANESİ');
            
            INSERT INTO servisler (id, firma_id, ad, kod, aciklama) VALUES 
            (1, 1, 'Laboratory', 'LAB', 'All blood and urine tests'),
            (2, 1, 'Pharmacy', 'PHR', 'Medication pickup'),
            (3, 1, 'Registration', 'REG', 'New patient registration');
            
            INSERT INTO kuyruklar (id, servis_id, ad, kod, oncelik) VALUES
            (1, 1, 'Blood Test', 'A', 0),
            (2, 2, 'Pickup', 'B', 0),
            (3, 3, 'Patient Reg', 'C', 0);
            
            -- Şifre: admin123 (bcrypt hash)
            INSERT INTO kullanicilar (id, firma_id, email, ad_soyad, rol, sifre_hash) VALUES
            (1, 1, 'admin@demo.com', 'Admin User', 'admin', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW');
            
            -- Sequence senkronizasyonu (ID'ler manuel girildiği için)
            SELECT setval('firmalar_id_seq', (SELECT MAX(id) FROM firmalar));
            SELECT setval('servisler_id_seq', (SELECT MAX(id) FROM servisler));
            SELECT setval('kuyruklar_id_seq', (SELECT MAX(id) FROM kuyruklar));
            SELECT setval('kullanicilar_id_seq', (SELECT MAX(id) FROM kullanicilar));
        """)
        
        print("İşlem tamamlandı! ID'ler artık 1, 2, 3 formatında.")
        
    except Exception as e:
        print(f"HATA: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    reset_database()
