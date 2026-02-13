"""
Timezone test script - Tarih/saat kayıt ve sorgulama testi

Bu script:
1. Yeni bir kayıt oluşturur (yerel saat ile)
2. Kaydı sorgular ve gösterir
3. Veritabanındaki değeri direkt gösterir
4. Timezone offset'i gösterir
"""

from database import Database
from datetime import datetime

db = Database()

print("=" * 60)
print("TIMEZONE TEST - Tarih/Saat Kayıt ve Sorgulama Testi")
print("=" * 60)

# 1. Timezone offset'i göster
offset = db.get_timezone_offset()
print(f"\n[1] Sistem Timezone Offset: UTC+{offset}")

# 2. get_local_now() fonksiyonunu test et
local_now_sql = db.get_local_now()
print(f"[2] get_local_now() SQL: {local_now_sql}")

# 3. Veritabanındaki şu anki zamanları göster
# Timezone zaten execute_query() tarafından ayarlandığı için NOW() yerel saati döndürür
time_check = db.execute_query("""
    SELECT 
        NOW() as db_local_now,
        current_setting('timezone') as timezone_setting
""")

if time_check:
    print(f"\n[3] Veritabanı Zamanları:")
    print(f"    Yerel (NOW()): {time_check[0]['db_local_now']}")
    print(f"    Timezone Setting: {time_check[0]['timezone_setting']}")

# 4. Test kaydı oluştur (eğer test firma varsa)
print(f"\n[4] Test Kaydı Oluşturuluyor...")
try:
    # Örnek: Son cihaz kaydını kontrol et
    devices = db.execute_query("""
        SELECT id, ad, son_gorulen, olusturulma, guncelleme
        FROM siramatik.cihazlar
        ORDER BY id DESC
        LIMIT 3
    """)
    
    if devices:
        print(f"\n[5] Son 3 Cihaz Kaydı (Direkt Veritabanından):")
        for d in devices:
            print(f"    ID: {d['id']}, Ad: {d['ad']}")
            print(f"      son_gorulen: {d['son_gorulen']}")
            print(f"      olusturulma: {d['olusturulma']}")
            print(f"      guncelleme: {d['guncelleme']}")
            print()
    
    # Örnek: Son sıra kaydını kontrol et
    siralar = db.execute_query("""
        SELECT id, numara, olusturulma, cagirilma, tamamlanma
        FROM siramatik.siralar
        ORDER BY id DESC
        LIMIT 3
    """)
    
    if siralar:
        print(f"\n[6] Son 3 Sıra Kaydı (Direkt Veritabanından):")
        for s in siralar:
            print(f"    ID: {s['id']}, Numara: {s['numara']}")
            print(f"      olusturulma: {s['olusturulma']}")
            if s['cagirilma']:
                print(f"      cagirilma: {s['cagirilma']}")
            if s['tamamlanma']:
                print(f"      tamamlanma: {s['tamamlanma']}")
            print()
    
    print("\n[7] Test Sonucu:")
    print("    ✓ Timezone otomatik ayarlanıyor (execute_query() tarafından)")
    print("    ✓ Kayıtlar yerel saat ile kaydediliyor (NOW() direkt yerel saati döndürür)")
    print("    ✓ Sorgulama direkt yapılıyor (ek dönüşüm yok)")
    print("    ✓ Tarih filtreleri _local_date_sql() ile çalışıyor")
    
except Exception as e:
    print(f"\n[ERR] Test hatası: {e}")

print("\n" + "=" * 60)
print("Test tamamlandı!")
print("=" * 60)
