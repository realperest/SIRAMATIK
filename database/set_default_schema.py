"""
Supabase Default Schema'yı Siramatik Yap
SQL ile PostgREST ayarlarını güncelle
"""
from sqlalchemy import create_engine, text

DB_URL = "postgresql://postgres.wyursjdrnnjabpfeucyi:qk4SEnyhu3NUk2@aws-1-eu-central-1.pooler.supabase.com:6543/postgres"

print("🔧 Supabase Default Schema Ayarı\n")

try:
    engine = create_engine(DB_URL, echo=False)
    
    with engine.connect() as conn:
        print("1️⃣ PostgreSQL rolleri için search_path ayarlanıyor...\n")
        
        # PostgREST'in kullandığı roller için search_path'i siramatik yap
        roles = ['authenticator', 'anon', 'authenticated', 'postgres']
        
        for role in roles:
            try:
                conn.execute(text(f"ALTER ROLE {role} SET search_path TO siramatik, public;"))
                print(f"   ✅ {role} rolü: search_path = siramatik, public")
            except Exception as e:
                print(f"   ⚠️  {role}: {str(e)[:80]}")
        
        conn.commit()
        
        print("\n2️⃣ Mevcut session için search_path ayarlanıyor...")
        conn.execute(text("SET search_path TO siramatik, public;"))
        print("   ✅ Session search_path = siramatik, public")
        
        print("\n3️⃣ Test ediliyor...")
        result = conn.execute(text("SHOW search_path;"))
        search_path = result.fetchone()[0]
        print(f"   📊 Mevcut search_path: {search_path}")
        
        # Tablo sayısını kontrol et
        result = conn.execute(text("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'siramatik'
        """))
        count = result.fetchone()[0]
        print(f"   📊 Siramatik schema'da {count} tablo var")
        
        print("\n" + "="*60)
        print("✅ AYARLAR TAMAMLANDI!")
        print("="*60)
        print("\n📝 Sonraki Adımlar:")
        print("1. Supabase servislerini yeniden başlatın (otomatik olabilir)")
        print("2. Backend'i yeniden başlatın:")
        print("   cd backend && python main.py")
        print("3. Test edin:")
        print("   python test_backend_schema.py")
        print()
        
except Exception as e:
    print(f"❌ Hata: {e}")
    import traceback
    traceback.print_exc()
