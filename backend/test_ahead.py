from database import db
import json

def test_query():
    # Simulate the query for ticket E033 (id: 4389 or similar)
    # Tickets created at 2026-02-07 22:xx UTC
    # Start of day (TR) is 2026-02-07 21:00 UTC
    
    tr_start = "2026-02-07 21:00:00+00"
    
    # Let's pick a ticket and see how many are "ahead"
    # Say we are looking at ID 4389 (E032)
    # We want to see how many are ahead of it in the SAME kuyruk
    
    # First get info for 4389
    me = db.execute_query("SELECT * FROM siramatik.siralar WHERE numara = 'E032'")[0]
    
    # Real query logic:
    # (oncelik > me.oncelik) OR (oncelik == me.oncelik AND olusturulma < me.olusturulma)
    
    query = """
        SELECT count(*) 
        FROM siramatik.siralar 
        WHERE kuyruk_id = :kid 
        AND durum = 'waiting' 
        AND olusturulma >= :start
        AND (
            oncelik > :my_oncelik 
            OR (oncelik = :my_oncelik AND olusturulma < :my_olusturulma)
        )
    """
    
    params = {
        "kid": me['kuyruk_id'],
        "start": tr_start,
        "my_oncelik": me['oncelik'],
        "my_olusturulma": me['olusturulma']
    }
    
    res = db.execute_query(query, params)
    print(f"Me: {me['numara']}, ID: {me['id']}, Created: {me['olusturulma']}")
    print(f"Start: {tr_start}")
    print(f"Result: {res}")

    # Let's see what's in the queue
    queue = db.execute_query("""
        SELECT id, numara, oncelik, olusturulma, durum 
        FROM siramatik.siralar 
        WHERE kuyruk_id = :kid 
        AND olusturulma >= :start
        ORDER BY oncelik DESC, olusturulma ASC
    """, {"kid": me['kuyruk_id'], "start": tr_start})
    print("\nFull Queue:")
    print(json.dumps(queue, indent=2, default=str))

if __name__ == "__main__":
    test_query()
