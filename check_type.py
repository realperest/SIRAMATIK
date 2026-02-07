
from database import db
res = db.execute_query("SELECT firma_id FROM siramatik.servisler LIMIT 1")
print(f"Data: {res}")
if res:
    print(f"Type: {type(res[0]['firma_id'])}")
