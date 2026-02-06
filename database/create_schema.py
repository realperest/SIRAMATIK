"""
Sıramatik Schema Kurulumu - Basit Versiyon
"""
from sqlalchemy import create_engine, text

DB_URL = "postgresql://postgres.wyursjdrnnjabpfeucyi:qk4SEnyhu3NUk2@aws-1-eu-central-1.pooler.supabase.com:6543/postgres"

print("🔧 Siramatik Schema Kurulumu\n")

try:
    engine = create_engine(DB_URL, echo=False)
    
    with engine.connect() as conn:
        # 1. Schema oluştur
        print("1️⃣ Schema oluşturuluyor...")
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS siramatik;"))
        conn.commit()
        print("   ✅ siramatik schema hazır\n")
        
        # 2. Search path ayarla
        print("2️⃣ Search path ayarlanıyor...")
        conn.execute(text("SET search_path TO siramatik, public;"))
        print("   ✅ Search path: siramatik, public\n")
        
        # 3. Kontrol
        print("3️⃣ Mevcut tablolar kontrol ediliyor...")
        result = conn.execute(text("""
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_schema IN ('public', 'siramatik')
            AND table_name IN ('firmalar', 'servisler', 'kuyruklar', 'siralar')
            ORDER BY table_schema, table_name;
        """))
        
        tables = list(result)
        if tables:
            print(f"   📊 {len(tables)} tablo bulundu:")
            for schema, table in tables:
                print(f"      - {schema}.{table}")
        else:
            print("   ⚠️  Henüz tablo yok")
        
        print("\n✅ Hazır! Şimdi SQL dosyalarını çalıştırabilirsiniz.")
        print("\n📝 Sonraki adım:")
        print("   python setup_supabase.py")
        
except Exception as e:
    print(f"❌ Hata: {e}")
