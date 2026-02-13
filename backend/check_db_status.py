
from database import db
from datetime import datetime
import json

def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError ("Type not serializable")

print("--- DB TIME CHECK ---")
# Timezone zaten execute_query() tarafından ayarlandığı için NOW() yerel saati döndürür
time_check = db.execute_query("SELECT NOW() as local_now, current_setting('timezone') as timezone_setting")
print(f"DB Server Local Time (NOW()): {time_check[0]['local_now']}")
print(f"DB Server Timezone Setting: {time_check[0]['timezone_setting']}")

print("\n--- DEVICES ---")
devices = db.execute_query("SELECT id, ad, cihaz_tipi, kullanim_tipi, durum, son_gorulen, metadata FROM siramatik.cihazlar")
for d in devices:
    print(json.dumps(dict(d), default=json_serial, indent=2))
