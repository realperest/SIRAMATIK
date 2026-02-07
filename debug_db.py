from backend.database import db
import json
from datetime import datetime

def debug_stats():
    firma_id = 1
    # Check total counts
    totals = db.execute_query("SELECT count(*) as total FROM siramatik.siralar WHERE firma_id = :f", {"f": firma_id})
    # Check today's date in DB
    db_date = db.execute_query("SELECT CURRENT_DATE as d, NOW() as n")[0]
    # Check today's counts
    today = db.execute_query("SELECT count(*) as total_today FROM siramatik.siralar WHERE firma_id = :f AND DATE(olusturulma) = CURRENT_DATE", {"f": firma_id})
    
    # Check some rows
    rows = db.execute_query("SELECT id, numara, durum, olusturulma FROM siramatik.siralar WHERE firma_id = :f ORDER BY olusturulma DESC LIMIT 5", {"f": firma_id})
    
    print(json.dumps({
        "totals": totals,
        "db_date": str(db_date),
        "today_stats": today,
        "recent_rows": rows
    }, indent=2, default=str))

if __name__ == "__main__":
    debug_stats()
