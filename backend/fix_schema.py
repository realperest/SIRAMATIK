
from sqlalchemy import create_engine, text

# Connection string from database.py
DB_URL = "postgresql://postgres.wyursjdrnnjabpfeucyi:qk4SEnyhu3NUk2@aws-1-eu-central-1.pooler.supabase.com:6543/postgres"

def fix_permissions():
    print("Connecting to database...")
    engine = create_engine(DB_URL)
    
    sql_commands = [
        "GRANT USAGE ON SCHEMA siramatik TO anon, authenticated, service_role;",
        "GRANT ALL ON ALL TABLES IN SCHEMA siramatik TO anon, authenticated, service_role;",
        "GRANT ALL ON ALL SEQUENCES IN SCHEMA siramatik TO anon, authenticated, service_role;",
        "ALTER DEFAULT PRIVILEGES IN SCHEMA siramatik GRANT ALL ON TABLES TO anon, authenticated, service_role;",
        "ALTER DEFAULT PRIVILEGES IN SCHEMA siramatik GRANT ALL ON SEQUENCES TO anon, authenticated, service_role;",
        "NOTIFY pgrst, 'reload schema';"  # Refresh PostgREST cache
    ]
    
    with engine.connect() as conn:
        for sql in sql_commands:
            try:
                print(f"Executing: {sql}")
                conn.execute(text(sql))
                conn.commit()
                print("Success.")
            except Exception as e:
                print(f"Error executing {sql}: {e}")

    print("Permissions updated and Schema Cache reloaded.")

if __name__ == "__main__":
    fix_permissions()
