
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "backend"))
from database import db

def check_schema():
    try:
        res = db.execute_query("SELECT * FROM siramatik.servisler LIMIT 1")
        if res:
            print("Columns:", res[0].keys())
        else:
            print("Tablo boş, ama sorgu çalıştı.")
            # Boşsa kolon adlarını alamayız bu yöntemle.
            # Information schema'ya bakalım
            res2 = db.execute_query("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_schema = 'siramatik' 
                AND table_name = 'servisler'
            """)
            print("Schema Columns:", [r['column_name'] for r in res2])
            
    except Exception as e:
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    check_schema()
