"""
Sıramatik Schema'ya Geçiş
Tabloları public'ten siramatik schema'sına taşı
"""
from sqlalchemy import create_engine, text
import os

# YAPLUS yöntemi - aws-1 pooler çalışıyor
DB_URL = "postgresql://postgres.wyursjdrnnjabpfeucyi:qk4SEnyhu3NUk2@aws-1-eu-central-1.pooler.supabase.com:6543/postgres"

DB_DIR = os.path.dirname(__file__)

def read_sql_file(filename):
    """SQL dosyasını oku"""
    filepath = os.path.join(DB_DIR, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def main():
    """Schema'ya geçiş"""
    print("\n" + "="*60)
    print("🔄 SIRAMATIK SCHEMA'YA GEÇİŞ")
    print("="*60)
    print()
    
    try:
        engine = create_engine(DB_URL, echo=False)
        
        print("1️⃣ Bağlantı test ediliyor...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT NOW();"))
            print(f"   ✅ Bağlantı başarılı!")
        
        # Adım 1: Eski tabloları sil
        print("\n2️⃣ Public schema'daki eski tabloları siliniyor...")
        with engine.connect() as conn:
            # Önce foreign key'ler için sırayla sil
            tables = [
                'cihaz_olaylari',
                'cihazlar',
                'siralar',
                'kullanicilar',
                'kuyruklar',
                'servisler',
                'firmalar',
                'sistem_ayarlari'
            ]
            
            for table in tables:
                try:
                    conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE;"))
                    print(f"   ✅ {table} silindi")
                except Exception as e:
                    print(f"   ⚠️  {table}: {str(e)[:50]}")
            
            conn.commit()
        
        print("\n3️⃣ Siramatik schema oluşturuluyor...")
        with engine.connect() as conn:
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS siramatik;"))
            conn.commit()
            print("   ✅ Schema oluşturuldu")
        
        # Adım 2: Orijinal SQL dosyalarını çalıştır (siramatik. önekli)
        sql_files = [
            ("01_schema.sql", "Schema"),
            ("02_tables.sql", "Tablolar (siramatik schema)"),
            ("03_indexes.sql", "İndeksler"),
            ("04_functions.sql", "Fonksiyonlar"),
            ("05_seed_data.sql", "Demo Veriler"),
        ]
        
        for filename, description in sql_files:
            print(f"\n{'='*60}")
            print(f"📝 {description}")
            print(f"{'='*60}")
            
            try:
                sql = read_sql_file(filename)
                
                with engine.connect() as conn:
                    conn.execute(text(sql))
                    conn.commit()
                
                print(f"✅ Başarılı!")
                
            except Exception as e:
                print(f"❌ Hata: {str(e)[:200]}")
                if "already exists" in str(e):
                    print("   ⚠️  Zaten var, devam ediliyor...")
                else:
                    user_input = input("Devam etmek istiyor musunuz? (e/h): ")
                    if user_input.lower() != 'e':
                        break
        
        print("\n" + "="*60)
        print("🎉 SCHEMA GEÇİŞİ TAMAMLANDI!")
        print("="*60)
        
        # Kontrol et
        print("\n4️⃣ Kontrol ediliyor...")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'siramatik'
                ORDER BY table_name;
            """))
            
            tables = [row[0] for row in result]
            print(f"\n   📊 Siramatik schema'da {len(tables)} tablo:")
            for table in tables:
                print(f"      ✅ siramatik.{table}")
        
        print("\n🔧 Backend Güncelleme Gerekli:")
        print("   Backend'de database.py dosyasını güncellemelisiniz.")
        print("   Her tablo çağrısına '.schema('siramatik')' ekleyin.")
        print()
        
    except Exception as e:
        print(f"\n❌ HATA: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
