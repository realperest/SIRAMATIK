"""
Supabase Timezone Ayarı Scripti
Bu script Supabase veritabanında timezone'u ayarlar.
"""

from database import engine
from sqlalchemy import text

print("=" * 60)
print("SUPABASE TIMEZONE AYARI")
print("=" * 60)

try:
    with engine.connect() as conn:
        print("\n[1] Timezone ayarlanıyor...")
        
        # Timezone'u ayarla
        conn.execute(text("ALTER DATABASE postgres SET timezone TO 'Europe/Istanbul'"))
        conn.commit()
        
        print("    [OK] Timezone ayarlandi: Europe/Istanbul")
        
        # Kontrol et
        print("\n[2] Ayar kontrol ediliyor...")
        result = conn.execute(text("SELECT current_setting('timezone') as current_timezone, NOW() as current_time"))
        row = result.fetchone()
        
        if row:
            print(f"    Timezone: {row[0]}")
            print(f"    Su anki zaman: {row[1]}")
        
        print("\n" + "=" * 60)
        print("[OK] BASARILI!")
        print("=" * 60)
        print("""
Artık tüm NOW() çağrıları (hem backend hem frontend) yerel saati döndürecek.
Backend ve Frontend (Supabase client) aynı timezone'u kullanacaktır.
        """)
        
except Exception as e:
    print(f"\n[HATA] {e}")
    print("\nOlası nedenler:")
    print("1. Supabase Free tier'da ALTER DATABASE komutu calismayabilir (superuser gerekir)")
    print("2. Veritabani baglantisi basarisiz olabilir")
    print("\nAlternatif cozum:")
    print("- Supabase Dashboard > SQL Editor'den manuel olarak calistirin")
    print("- Veya connection string'de timezone ayarlanabilir (backend'de zaten yapildi)")
