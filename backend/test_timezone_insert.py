"""Timezone test - Yeni kayıt oluştur ve kontrol et"""
from database import Database
from datetime import datetime

db = Database()

print("=" * 60)
print("TIMEZONE TEST - YENI KAYIT OLUSTURMA")
print("=" * 60)

# Mevcut zaman
print(f"\n[1] Python datetime.now(): {datetime.now()}")

# Veritabanındaki NOW()
result = db.execute_query("SELECT NOW() as db_now, current_setting('timezone') as tz")
if result:
    print(f"[2] Veritabanı NOW(): {result[0]['db_now']}")
    print(f"[3] Veritabanı Timezone: {result[0]['tz']}")

# Test: Yeni bir cihaz kaydı oluştur (heartbeat)
print(f"\n[4] Test cihaz heartbeat gönderiliyor...")
try:
    # Mevcut bir cihaz ID'si al
    devices = db.execute_query("SELECT id FROM siramatik.cihazlar LIMIT 1")
    if devices:
        device_id = devices[0]['id']
        success = db.device_heartbeat(device_id, ip="127.0.0.1")
        if success:
            print(f"    [OK] Heartbeat gönderildi: device_id={device_id}")
            
            # Son görülme zamanını kontrol et
            result = db.execute_query(
                "SELECT son_gorulen FROM siramatik.cihazlar WHERE id = :id",
                {"id": device_id}
            )
            if result:
                print(f"    [KONTROL] son_gorulen: {result[0]['son_gorulen']}")
                print(f"    [KONTROL] Python zamanı: {datetime.now()}")
                
                # Farkı hesapla
                db_time = result[0]['son_gorulen']
                py_time = datetime.now()
                
                # db_time datetime objesi ise direkt kullan
                if hasattr(db_time, 'timestamp'):
                    diff = abs((py_time - db_time).total_seconds())
                else:
                    # String ise parse et
                    try:
                        if isinstance(db_time, str):
                            # ISO format: 2026-02-13 11:39:00.123456+03:00
                            db_time_parsed = datetime.fromisoformat(db_time.replace('Z', '+00:00'))
                            diff = abs((py_time - db_time_parsed).total_seconds())
                        else:
                            diff = 0
                    except:
                        diff = 999999
                
                print(f"    [FARK] {diff:.0f} saniye")
                
                if diff < 60:
                    print(f"    [OK] Zamanlar uyumlu! (60 saniyeden az fark)")
                else:
                    print(f"    [UYARI] Zamanlar uyumsuz! (60 saniyeden fazla fark)")
        else:
            print(f"    [HATA] Heartbeat gönderilemedi")
    else:
        print(f"    [UYARI] Test için cihaz bulunamadı")
except Exception as e:
    print(f"    [HATA] {e}")

print("\n" + "=" * 60)
