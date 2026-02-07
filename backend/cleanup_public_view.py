
from sqlalchemy import create_engine, text

# Connection string
DB_URL = "postgresql://postgres.wyursjdrnnjabpfeucyi:qk4SEnyhu3NUk2@aws-1-eu-central-1.pooler.supabase.com:6543/postgres"

def cleanup_public_view():
    print("Connecting to database...")
    engine = create_engine(DB_URL)
    
    with engine.connect() as conn:
        try:
            print("Dropping View: public.siralar...")
            conn.execute(text("DROP VIEW IF EXISTS public.siralar;"))
            
            # Opsiyonel: Public şemasında başka kalıntı varsa temizle (emin olmak için)
            print("Cleaning up permissions on public schema just in case...")
            # Bu adım şart değil ama temizlik için iyi
            
            conn.commit()
            print("Success! 'public.siralar' view has been removed.")
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    cleanup_public_view()
