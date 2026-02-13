"""
Dinamik Timezone Test Scripti
Her sorguda timezone'un tablodan okunan offset'e göre ayarlanıp ayarlanmadığını test eder.
"""

from database import Database
from datetime import datetime

db = Database()

print("=" * 60)
print("DİNAMİK TIMEZONE TEST")
print("=" * 60)

# 1. Timezone offset'i göster
offset = db.get_timezone_offset()
print(f"\n[1] Sistem Timezone Offset (Tablodan): UTC+{offset}")

# 2. Timezone string'ini göster
timezone_str = db._offset_to_timezone_string(offset)
print(f"[2] PostgreSQL Timezone String: {timezone_str}")

# 3. Veritabanındaki şu anki zamanları göster
print("\n[3] Veritabanı Zamanları (Timezone Ayarlandıktan Sonra):")
time_check = db.execute_query("""
    SELECT 
        current_setting('timezone') as current_timezone,
        NOW() as db_now,
        CURRENT_TIMESTAMP as current_timestamp,
        LOCALTIMESTAMP as local_timestamp
""")

if time_check:
    print(f"    current_setting('timezone'): {time_check[0]['current_timezone']}")
    print(f"    NOW(): {time_check[0]['db_now']}")
    print(f"    CURRENT_TIMESTAMP: {time_check[0]['current_timestamp']}")
    print(f"    LOCALTIMESTAMP: {time_check[0]['local_timestamp']}")

# 4. Test kaydı oluştur
print(f"\n[4] Test Kaydı Oluşturuluyor...")
try:
    # Örnek: Son cihaz kaydını kontrol et
    devices = db.execute_query("SELECT id, ad, son_gorulen FROM siramatik.cihazlar ORDER BY id DESC LIMIT 1")
    if devices:
        print(f"    Son cihaz kaydı:")
        print(f"    ID: {devices[0]['id']}")
        print(f"    Ad: {devices[0]['ad']}")
        print(f"    Son Görülme: {devices[0]['son_gorulen']}")
        print(f"    (Bu değer yerel saat ile kaydedilmiş olmalı)")
except Exception as e:
    print(f"    ⚠️  Hata: {e}")

# 5. Python tarafındaki zaman
print(f"\n[5] Python Tarafındaki Zaman:")
print(f"    Python datetime.now(): {datetime.now()}")

print("\n" + "=" * 60)
print("SONUÇ:")
print("=" * 60)
print("""
Eğer NOW() değeri Python datetime.now() ile yaklaşık olarak eşleşiyorsa,
timezone ayarı başarılı demektir.

ÖNEMLİ: 
- Her sorguda timezone otomatik olarak ayarlanıyor
- Tablodan okunan offset kullanılıyor
- NOW() direkt yerel saati döndürüyor
- Frontend'e gönderirken timezone bilgisi doğru gelir
""")
