
from sqlalchemy import create_engine, text

# Connection string
# Dikkat: Bu connection string, veritabanı sahibi (postgres) yetkisine sahiptir.
# Bu sayede 'ALTER ROLE' komutunu çalıştırabiliriz.
DB_URL = "postgresql://postgres.wyursjdrnnjabpfeucyi:qk4SEnyhu3NUk2@aws-1-eu-central-1.pooler.supabase.com:6543/postgres"

def fix_api_exposed_schemas():
    print("Connecting to database as superuser...")
    engine = create_engine(DB_URL)
    
    with engine.connect() as conn:
        try:
            # 1. API kullanıcısının (authenticator) görebildiği şemaları ayarla
            # Bu, Dashboard'daki "Exposed schemas" ayarının SQL karşılığıdır.
            print("Extending exposed schemas for API role...")
            conn.execute(text("ALTER ROLE authenticator SET pgrst.db_schemas TO 'public, siramatik';"))
            conn.execute(text("GRANT USAGE ON SCHEMA siramatik TO anon, authenticated, service_role;"))
            conn.execute(text("GRANT ALL ON ALL TABLES IN SCHEMA siramatik TO anon, authenticated, service_role;"))
            
            # 2. Değişikliklerin etkili olması için konfigürasyonu yeniden yükle
            print("Reloading API configuration...")
            conn.execute(text("NOTIFY pgrst, 'reload config';"))
            
            conn.commit()
            print("Success! 'siramatik' schema should now be exposed to the API.")
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    fix_api_exposed_schemas()
