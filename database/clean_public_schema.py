"""
Public Schema Temizleme
Siramatik schema'da tablolar var, public'tekileri silelim
"""
from sqlalchemy import create_engine, text

DB_URL = "postgresql://postgres.wyursjdrnnjabpfeucyi:qk4SEnyhu3NUk2@aws-1-eu-central-1.pooler.supabase.com:6543/postgres"

print("🧹 Public Schema Temizleme\n")

try:
    engine = create_engine(DB_URL, echo=False)
    
    with engine.connect() as conn:
        # Public schema'daki tabloları sil
        print("1️⃣ Public schema'daki tablolar siliniyor...\n")
        
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
                conn.execute(text(f"DROP TABLE IF EXISTS public.{table} CASCADE;"))
                print(f"   ✅ public.{table} silindi")
            except Exception as e:
                print(f"   ⚠️  {table}: {str(e)[:80]}")
        
        conn.commit()
        
        print("\n2️⃣ Kontrol ediliyor...\n")
        
        # Public schema kontrol
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_name IN ('firmalar', 'servisler', 'kuyruklar', 'siralar', 'kullanicilar', 'cihazlar', 'cihaz_olaylari', 'sistem_ayarlari')
        """))
        
        public_tables = [row[0] for row in result]
        
        if public_tables:
            print(f"   ⚠️  Public'te hala {len(public_tables)} tablo var:")
            for t in public_tables:
                print(f"      - {t}")
        else:
            print("   ✅ Public schema temiz!")
        
        # Siramatik schema kontrol
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'siramatik'
            ORDER BY table_name
        """))
        
        siramatik_tables = [row[0] for row in result]
        
        print(f"\n   ✅ Siramatik schema'da {len(siramatik_tables)} tablo:")
        for t in siramatik_tables:
            print(f"      - siramatik.{t}")
        
        print("\n✅ Temizlik tamamlandı!")
        print("\n📝 Şimdi backend'i siramatik schema için yapılandırmalısınız.")
        
except Exception as e:
    print(f"❌ Hata: {e}")
    import traceback
    traceback.print_exc()
