"""
Sıramatik - Supabase Bağlantı Testi
Önce bağlantıyı test edelim
"""
import psycopg2

# Resimden alınan connection string
# Transaction pooler
conn_str_transaction = "postgresql://postgres.wyursjdrnnjabpfeucyi:qk4SEnyhu3NUk2@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"

# Session pooler  
conn_str_session = "postgresql://postgres.wyursjdrnnjabpfeucyi:qk4SEnyhu3NUk2@aws-0-eu-central-1.pooler.supabase.com:5432/postgres"

print("🔌 Supabase Bağlantı Testi\n")

# Transaction pooler dene
print("1️⃣ Transaction Pooler (port 6543) deneniyor...")
try:
    conn = psycopg2.connect(conn_str_transaction)
    cursor = conn.cursor()
    cursor.execute("SELECT NOW();")
    result = cursor.fetchone()
    print(f"   ✅ BAŞARILI! Sunucu zamanı: {result[0]}")
    cursor.close()
    conn.close()
    print("\n🎉 Transaction pooler çalışıyor! Kuruluma devam edebiliriz.\n")
    exit(0)
except Exception as e:
    print(f"   ❌ Başarısız: {e}\n")

# Session pooler dene
print("2️⃣ Session Pooler (port 5432) deneniyor...")
try:
    conn = psycopg2.connect(conn_str_session)
    cursor = conn.cursor()
    cursor.execute("SELECT NOW();")
    result = cursor.fetchone()
    print(f"   ✅ BAŞARILI! Sunucu zamanı: {result[0]}")
    cursor.close()
    conn.close()
    print("\n🎉 Session pooler çalışıyor! Kuruluma devam edebiliriz.\n")
    exit(0)
except Exception as e:
    print(f"   ❌ Başarısız: {e}\n")

print("❌ Her iki pooler de başarısız oldu.")
print("\n💡 Çözüm Önerileri:")
print("1. Supabase Dashboard > Settings > Database'de IPv4 add-on aktif mi kontrol edin")
print("2. Şifrenin doğru olduğundan emin olun")
print("3. Firewall/VPN bağlantıyı engelliyor olabilir")
print("\n📝 Manuel kurulum için:")
print("   https://supabase.com/dashboard/project/wyursjdrnnjabpfeucyi/sql")
print("   SQL Editor'de database/*.sql dosyalarını sırayla çalıştırın")
