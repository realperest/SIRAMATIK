
from sqlalchemy import create_engine, text

# Connection string
DB_URL = "postgresql://postgres.wyursjdrnnjabpfeucyi:qk4SEnyhu3NUk2@aws-1-eu-central-1.pooler.supabase.com:6543/postgres"

def expose_siramatik_schema():
    """
    PostgREST'in 'siramatik' şemasını görebilmesi için gerekli ayarları yapar.
    
    Bu işlem, Supabase Dashboard -> Settings -> API -> Exposed schemas 
    ayarının SQL karşılığıdır.
    """
    print("Connecting to database as superuser...")
    engine = create_engine(DB_URL)
    
    with engine.connect() as conn:
        try:
            # 1. PostgREST'in hangi şemaları tarayacağını belirle
            print("Setting PostgREST exposed schemas to 'public, siramatik'...")
            
            # authenticator rolü, PostgREST'in kullandığı ana roldür
            # Bu rolün görebildiği şemaları ayarlıyoruz
            conn.execute(text("""
                ALTER ROLE authenticator 
                SET pgrst.db_schemas = 'public, siramatik';
            """))
            
            # 2. Şema kullanım izinlerini ver
            print("Granting schema usage permissions...")
            conn.execute(text("GRANT USAGE ON SCHEMA siramatik TO anon, authenticated;"))
            
            # 3. Tablolara erişim izinlerini ver
            print("Granting table permissions...")
            conn.execute(text("GRANT ALL ON ALL TABLES IN SCHEMA siramatik TO anon, authenticated;"))
            conn.execute(text("GRANT ALL ON ALL SEQUENCES IN SCHEMA siramatik TO anon, authenticated;"))
            
            # 4. Gelecekte oluşturulacak tablolar için varsayılan izinleri ayarla
            print("Setting default privileges...")
            conn.execute(text("""
                ALTER DEFAULT PRIVILEGES IN SCHEMA siramatik 
                GRANT ALL ON TABLES TO anon, authenticated;
            """))
            conn.execute(text("""
                ALTER DEFAULT PRIVILEGES IN SCHEMA siramatik 
                GRANT ALL ON SEQUENCES TO anon, authenticated;
            """))
            
            # 5. PostgREST'i yeniden yükle (schema cache'i temizle)
            print("Reloading PostgREST configuration...")
            conn.execute(text("NOTIFY pgrst, 'reload config';"))
            conn.execute(text("NOTIFY pgrst, 'reload schema';"))
            
            conn.commit()
            
            print("\n✅ SUCCESS!")
            print("=" * 60)
            print("PostgREST configuration updated:")
            print("  - Exposed schemas: public, siramatik")
            print("  - Permissions granted to: anon, authenticated")
            print("  - Schema cache reloaded")
            print("=" * 60)
            print("\nPlease wait 5-10 seconds for PostgREST to reload,")
            print("then refresh your frontend page.")
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            print("\nIf you see a permission error, you may need to:")
            print("1. Go to Supabase Dashboard")
            print("2. Settings -> API -> Exposed schemas")
            print("3. Add 'siramatik' to the list")

if __name__ == "__main__":
    expose_siramatik_schema()
