
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv('D:/KODLAMALAR/GITHUB/SIRAMATIK/backend/.env')
DB_URL = "postgresql://postgres.wyursjdrnnjabpfeucyi:qk4SEnyhu3NUk2@aws-1-eu-central-1.pooler.supabase.com:6543/postgres"

engine = create_engine(DB_URL)

def debug_data():
    with engine.connect() as conn:
        print("--- SIRAMATIK.SIRALAR DATA (TOP 5) ---")
        res = conn.execute(text("SELECT id, numara, durum, firma_id, cagirilma FROM siramatik.siralar ORDER BY olusturulma DESC LIMIT 5"))
        for row in res:
            print(row)
            
        print("\n--- SIRAMATIK.SIRALAR 'calling' STATUS ---")
        res = conn.execute(text("SELECT id, numara, firma_id FROM siramatik.siralar WHERE durum = 'calling'"))
        rows = res.fetchall()
        print(f"Total calling: {len(rows)}")
        for row in rows:
            print(row)

if __name__ == "__main__":
    debug_data()
