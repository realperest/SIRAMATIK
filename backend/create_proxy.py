
from sqlalchemy import create_engine, text

# Connection string
DB_URL = "postgresql://postgres.wyursjdrnnjabpfeucyi:qk4SEnyhu3NUk2@aws-1-eu-central-1.pooler.supabase.com:6543/postgres"

def create_proxy_views():
    print("Connecting to database...")
    engine = create_engine(DB_URL)
    
    with engine.connect() as conn:
        # 1. 'siralar' Tablosu için Proxy View
        print("Creating View: public.siralar -> siramatik.siralar")
        conn.execute(text("""
            CREATE OR REPLACE VIEW public.siralar AS 
            SELECT * FROM siramatik.siralar;
        """))
        
        # 2. İzinleri Ver (Anonim erişim için)
        print("Granting permissions...")
        conn.execute(text("GRANT SELECT ON public.siralar TO anon, authenticated, service_role;"))
        
        # 3. Cache Temizle
        conn.execute(text("NOTIFY pgrst, 'reload schema';"))
        
        conn.commit()
    
    print("Proxy views created successfully. Frontend can now access 'public.siralar' which reads from 'siramatik.siralar'.")

if __name__ == "__main__":
    create_proxy_views()
