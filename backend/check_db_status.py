
from database import db
from datetime import datetime
import json

def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError ("Type not serializable")

print("--- DB TIME CHECK ---")
time_check = db.execute_query("SELECT NOW() as utc_now, (NOW() + INTERVAL '3 hours') as tsi_now")
print(f"DB Server UTC: {time_check[0]['utc_now']}")
print(f"DB Server TSI: {time_check[0]['tsi_now']}")

print("\n--- DEVICES ---")
devices = db.execute_query("SELECT id, ad, tip, durum, son_gorulen, metadata FROM siramatik.cihazlar")
for d in devices:
    print(json.dumps(dict(d), default=json_serial, indent=2))
