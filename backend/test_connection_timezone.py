"""Connection string timezone test"""
from database import engine
from sqlalchemy import text
from sqlalchemy.orm import Session

print("=" * 60)
print("CONNECTION STRING TIMEZONE TEST")
print("=" * 60)

# Yeni bir connection aç (connection string'deki timezone ile)
with Session(engine) as session:
    # Timezone'u kontrol et
    result = session.execute(text("SELECT current_setting('timezone') as tz, NOW() as now"))
    row = result.fetchone()
    
    print(f"\n[1] Connection String Timezone:")
    print(f"    Timezone: {row[0]}")
    print(f"    NOW(): {row[1]}")
    
    # Python zamanı ile karşılaştır
    from datetime import datetime, timezone
    py_now = datetime.now()
    print(f"\n[2] Python datetime.now(): {py_now}")
    
    # Farkı hesapla (timezone-aware karşılaştırma)
    db_time = row[1]
    if hasattr(db_time, 'replace'):
        # timezone-aware datetime
        if db_time.tzinfo is None:
            # timezone-naive ise UTC varsay
            db_time_utc = db_time.replace(tzinfo=timezone.utc)
        else:
            db_time_utc = db_time
        
        # Python datetime'ı timezone-aware yap
        if py_now.tzinfo is None:
            # Yerel timezone için UTC+3 varsay
            py_now_aware = py_now.replace(tzinfo=timezone.utc).replace(hour=py_now.hour-3)
        else:
            py_now_aware = py_now
        
        # Basit saat karşılaştırması
        db_hour = db_time_utc.hour
        py_hour = py_now.hour
        diff_hours = abs(db_hour - py_hour)
        if diff_hours > 12:
            diff_hours = 24 - diff_hours
        
        print(f"\n[3] Saat Karşılaştırması:")
        print(f"    DB Saati: {db_hour:02d}:{db_time_utc.minute:02d}")
        print(f"    Python Saati: {py_hour:02d}:{py_now.minute:02d}")
        print(f"    Fark: {diff_hours} saat")
        
        if diff_hours <= 1:
            print(f"    [OK] Zamanlar uyumlu!")
        else:
            print(f"    [HATA] Zamanlar uyumsuz! ({diff_hours} saat fark)")

print("\n" + "=" * 60)
