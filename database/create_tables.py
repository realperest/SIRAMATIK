"""
Supabase Tablo Oluşturma
Supabase Management API veya SQL API kullanarak
"""
import requests
import json

SUPABASE_URL = "https://wyursjdrnnjabpfeucyi.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind5dXJzamRybm5qYWJwZmV1Y3lpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk4NzcwOTEsImV4cCI6MjA4NTQ1MzA5MX0.uacZI2vB1pfDyk_UO0lvJBgftJl_R04YX9Bv9kWOLd4"
DB_PASSWORD = "qk4SEnyhu3NUk2"

print("="*60)
print("🔧 SUPABASE TABLO OLUŞTURMA")
print("="*60)
print()

# SQL dosyalarını oku
import os

db_dir = os.path.dirname(__file__)

sql_files = [
    ("02_tables_public.sql", "Tablolar"),
    ("03_indexes_public.sql", "İndeksler"),
    ("04_functions_public.sql", "Fonksiyonlar"),
    ("05_seed_data_public.sql", "Demo Veriler"),
]

print("📝 SQL Dosyaları:")
for filename, desc in sql_files:
    filepath = os.path.join(db_dir, filename)
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print(f"   ✅ {filename} ({size} bytes) - {desc}")
    else:
        print(f"   ❌ {filename} - BULUNAMADI!")

print("\n" + "="*60)
print("⚠️  DİKKAT: Supabase REST API ile DDL çalıştırılamaz!")
print("="*60)
print()
print("Supabase, güvenlik nedeniyle REST API üzerinden")
print("CREATE TABLE, CREATE FUNCTION gibi DDL komutlarını")
print("çalıştırmaya izin vermez.")
print()
print("💡 Çözüm: SQL Editor kullanmalısınız")
print()
print("🔗 SQL Editor:")
print("   https://supabase.com/dashboard/project/wyursjdrnnjabpfeucyi/sql")
print()
print("📋 Adımlar:")
print("   1. Yukarıdaki linke git")
print("   2. 'New query' tıkla")
print("   3. SQL dosyasını kopyala-yapıştır")
print("   4. 'RUN' bas")
print("   5. Sıradaki dosyaya geç")
print()
print("⏱️  Toplam süre: ~5 dakika")
print()

# Alternatif: psycopg2 ile direkt bağlantı
print("="*60)
print("🔄 ALTERNATİF: PostgreSQL Direkt Bağlantı")
print("="*60)
print()
print("Eğer IPv4 ağınız varsa, psycopg2 ile direkt bağlanıp")
print("SQL'leri otomatik çalıştırabiliriz.")
print()
print("Ama daha önce 'Tenant or user not found' hatası aldık.")
print("Bu yüzden manuel SQL Editor kullanmak en güvenli yol.")
print()
