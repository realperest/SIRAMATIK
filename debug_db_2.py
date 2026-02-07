from backend.database import db
import json
from collections import Counter

def debug_counts():
    firma_id = 1
    # Check frequency of ticket creation
    freq = db.execute_query("""
        SELECT to_char(olusturulma, 'YYYY-MM-DD HH24:MI') as dk, count(*) 
        FROM siramatik.siralar 
        WHERE firma_id = :f AND DATE(olusturulma) = CURRENT_DATE
        GROUP BY dk ORDER BY dk DESC LIMIT 20
    """, {"f": firma_id})
    
    # Check distinct kuyruk names
    queues = db.execute_query("""
        SELECT k.ad, count(*) 
        FROM siramatik.siralar s
        JOIN siramatik.kuyruklar k ON s.kuyruk_id = k.id
        WHERE s.firma_id = :f AND DATE(olusturulma) = CURRENT_DATE
        GROUP BY k.ad
    """, {"f": firma_id})

    print(json.dumps({
        "minute_frequency": freq,
        "queue_distribution": queues
    }, indent=2))

if __name__ == "__main__":
    debug_counts()
