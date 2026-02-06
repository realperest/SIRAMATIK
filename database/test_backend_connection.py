"""
Sıramatik - Supabase Bağlantı Test
Backend'in Supabase'e bağlanıp bağlanamadığını test eder
"""
import sys
import os

# Backend klasörünü path'e ekle
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from supabase import create_client
from dotenv import load_dotenv

# Backend .env dosyasını yükle
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

print("="*60)
print("🔌 SUPABASE REST API BAĞLANTI TESTİ")
print("="*60)
print(f"📍 URL: {SUPABASE_URL}")
print(f"🔑 Key: {SUPABASE_KEY[:20]}...")
print()

try:
    # Supabase client oluştur
    print("1️⃣ Supabase client oluşturuluyor...")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("   ✅ Client oluşturuldu")
    
    # Firmalar tablosunu oku (demo veri varsa)
    print("\n2️⃣ Firmalar tablosu okunuyor...")
    response = supabase.table('firmalar').select('*').execute()
    
    if response.data:
        print(f"   ✅ {len(response.data)} firma bulundu:")
        for firma in response.data:
            print(f"      - {firma.get('ad', 'İsimsiz')}")
    else:
        print("   ⚠️  Henüz firma verisi yok (normal, demo veriler eklenmemiş)")
    
    # Servisler tablosunu oku
    print("\n3️⃣ Servisler tablosu okunuyor...")
    response = supabase.table('servisler').select('*').execute()
    
    if response.data:
        print(f"   ✅ {len(response.data)} servis bulundu:")
        for servis in response.data:
            print(f"      - {servis.get('ad', 'İsimsiz')}")
    else:
        print("   ⚠️  Henüz servis verisi yok")
    
    # Kuyruklar tablosunu oku
    print("\n4️⃣ Kuyruklar tablosu okunuyor...")
    response = supabase.table('kuyruklar').select('*').execute()
    
    if response.data:
        print(f"   ✅ {len(response.data)} kuyruk bulundu:")
        for kuyruk in response.data:
            print(f"      - {kuyruk.get('ad', 'İsimsiz')} (Kod: {kuyruk.get('kod', '?')})")
    else:
        print("   ⚠️  Henüz kuyruk verisi yok")
    
    print("\n" + "="*60)
    print("🎉 BAŞARILI! Backend Supabase'e bağlanabilir.")
    print("="*60)
    print("\n✅ Supabase REST API çalışıyor")
    print("✅ Tablolar okunabiliyor")
    print("✅ Backend hazır!")
    print("\n🚀 Sonraki adım:")
    print("   cd backend && python main.py")
    print()
    
except Exception as e:
    print(f"\n❌ HATA: {e}")
    print("\n💡 Olası Nedenler:")
    print("1. SQL dosyaları henüz çalıştırılmamış")
    print("2. SUPABASE_URL veya SUPABASE_KEY yanlış")
    print("3. Tablolar 'siramatik' schema'sında değil 'public' schema'sında")
    print("\n🔧 Çözüm:")
    print("1. Supabase SQL Editor'de tabloları oluşturun")
    print("2. backend/.env dosyasını kontrol edin")
    print("3. Tabloların schema'sını kontrol edin:")
    print("   SELECT table_schema, table_name FROM information_schema.tables")
    print("   WHERE table_name IN ('firmalar', 'servisler', 'kuyruklar');")
    print()
    
    import traceback
    traceback.print_exc()
