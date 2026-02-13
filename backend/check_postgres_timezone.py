"""
PostgreSQL Timezone Kontrol ve Ayarlama Scripti
Supabase'de timezone ayarını kontrol eder ve değiştirmeyi dener.
"""

from database import Database, engine
from sqlalchemy import text

db = Database()

print("=" * 60)
print("POSTGRESQL TIMEZONE KONTROL")
print("=" * 60)

# 1. Mevcut timezone ayarını kontrol et
print("\n[1] Mevcut PostgreSQL Timezone Ayarları:")
timezone_info = db.execute_query("""
    SELECT 
        current_setting('timezone') as current_timezone,
        NOW() as db_now,
        CURRENT_TIMESTAMP as current_timestamp,
        LOCALTIMESTAMP as local_timestamp
""")

if timezone_info:
    print(f"    current_setting('timezone'): {timezone_info[0]['current_timezone']}")
    print(f"    NOW(): {timezone_info[0]['db_now']}")
    print(f"    CURRENT_TIMESTAMP: {timezone_info[0]['current_timestamp']}")
    print(f"    LOCALTIMESTAMP: {timezone_info[0]['local_timestamp']}")

# 2. Session seviyesinde timezone değiştirmeyi dene
print("\n[2] Session Seviyesinde Timezone Değiştirme Testi:")
try:
    with engine.connect() as conn:
        # Session seviyesinde timezone ayarla
        conn.execute(text("SET timezone = 'Europe/Istanbul'"))
        conn.commit()
        
        # Kontrol et
        result = conn.execute(text("""
            SELECT 
                current_setting('timezone') as session_timezone,
                NOW() as db_now_istanbul
        """))
        row = result.fetchone()
        if row:
            print(f"    Session timezone: {row[0]}")
            print(f"    NOW() (Istanbul): {row[1]}")
except Exception as e:
    print(f"    ❌ Hata: {e}")

# 3. Database seviyesinde timezone ayarlama (ALTER DATABASE) - Genellikle sadece superuser yapabilir
print("\n[3] Database Seviyesinde Timezone Ayarlama (Superuser Gerekli):")
try:
    with engine.connect() as conn:
        # Database seviyesinde timezone ayarlamayı dene
        result = conn.execute(text("""
            SELECT 
                current_database() as db_name,
                current_setting('timezone') as current_tz
        """))
        row = result.fetchone()
        if row:
            print(f"    Database: {row[0]}")
            print(f"    Mevcut timezone: {row[1]}")
            
        # ALTER DATABASE komutunu dene (genellikle başarısız olur çünkü superuser gerekir)
        try:
            conn.execute(text("ALTER DATABASE postgres SET timezone = 'Europe/Istanbul'"))
            conn.commit()
            print("    ✅ Database timezone ayarlandı!")
        except Exception as e:
            print(f"    ⚠️  Database timezone ayarlanamadı (normal, superuser gerekir): {e}")
except Exception as e:
    print(f"    ❌ Hata: {e}")

# 4. Connection string'de timezone ayarlama
print("\n[4] Connection String'de Timezone Ayarı:")
print("    PostgreSQL connection string'ine 'options=-c timezone=Europe/Istanbul' eklenebilir")
print("    Mevcut connect_args:")
print(f"    {db.engine.connect_args}")

# 5. Öneri
print("\n" + "=" * 60)
print("ÖNERİ:")
print("=" * 60)
print("""
Supabase'de timezone ayarını değiştirmek için:

1. **Connection String'de Ayar (ÖNERİLEN):**
   connect_args'a 'options=-c timezone=Europe/Istanbul' eklenebilir
   Bu her bağlantıda otomatik olarak timezone'u ayarlar.

2. **Her Sorguda Ayar:**
   Her sorgudan önce 'SET timezone = ...' çalıştırılabilir
   Ama bu her sorgu için ekstra bir komut demek.

3. **Supabase Dashboard'dan:**
   Supabase Dashboard > Settings > Database > Timezone
   (Eğer bu seçenek varsa)

4. **ALTER DATABASE (Superuser Gerekli):**
   Genellikle Supabase'de superuser yetkisi yoktur.
""")
