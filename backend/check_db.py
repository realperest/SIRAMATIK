from database import db
from datetime import datetime
import json

def check():
    res = db.execute_query("""
        SELECT 
            id, 
            numara, 
            olusturulma, 
            (olusturulma AT TIME ZONE 'Europe/Istanbul')::date as tr_tarihi,
            (NOW() AT TIME ZONE 'Europe/Istanbul')::date as suanki_tr_tarihi
        FROM siramatik.siralar 
        ORDER BY olusturulma DESC 
        LIMIT 10
    """)
    print(json.dumps(res, indent=2, default=str))

if __name__ == "__main__":
    check()
