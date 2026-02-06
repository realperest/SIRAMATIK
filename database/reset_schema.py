"""
Global Schema Ayarını Geri Al
"""
from sqlalchemy import create_engine, text

DB_URL = "postgresql://postgres.wyursjdrnnjabpfeucyi:qk4SEnyhu3NUk2@aws-1-eu-central-1.pooler.supabase.com:6543/postgres"

print("🔄 Global Schema Ayarını Geri Alıyorum\n")

try:
    engine = create_engine(DB_URL, echo=False)
    
    with engine.connect() as conn:
        # Rolleri public'e geri al
        roles = ['authenticator', 'anon', 'authenticated', 'postgres']
        
        for role in roles:
            try:
                conn.execute(text(f"ALTER ROLE {role} SET search_path TO public;"))
                print(f"   ✅ {role} → public")
            except Exception as e:
                print(f"   ⚠️  {role}: {str(e)[:50]}")
        
        conn.commit()
        print("\n✅ Global ayarlar public'e döndü")
        
except Exception as e:
    print(f"❌ Hata: {e}")
