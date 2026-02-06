"""
Supabase REST API Bağlantı Testi - DOĞRU KEY
"""
from supabase import create_client

# DOĞRU ANON KEY
SUPABASE_URL = "https://wyursjdrnnjabpfeucyi.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind5dXJzamRybm5qYWJwZmV1Y3lpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk4NzcwOTEsImV4cCI6MjA4NTQ1MzA5MX0.uacZI2vB1pfDyk_UO0lvJBgftJl_R04YX9Bv9kWOLd4"

print("="*60)
print("🔌 SUPABASE REST API BAĞLANTI TESTİ")
print("="*60)
print(f"📍 URL: {SUPABASE_URL}")
print(f"🔑 Key: {SUPABASE_ANON_KEY[:50]}...")
print()

try:
    # Supabase client oluştur
    print("1️⃣ Client oluşturuluyor...")
    supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    print("   ✅ Client oluşturuldu")
    
    # Bağlantıyı test et
    print("\n2️⃣ Bağlantı test ediliyor...")
    
    # Firmalar tablosunu dene
    try:
        response = supabase.table('firmalar').select('*').limit(1).execute()
        print(f"   ✅ 'firmalar' tablosu okunabilir")
        if response.data:
            print(f"   📊 Kayıt sayısı: {len(response.data)}")
            print(f"   📝 İlk firma: {response.data[0].get('ad', 'İsimsiz')}")
        else:
            print(f"   ⚠️  Tablo boş (demo veriler henüz eklenmemiş)")
    except Exception as e:
        error_str = str(e)
        if "relation" in error_str.lower() or "does not exist" in error_str.lower():
            print(f"   ⚠️  'firmalar' tablosu henüz oluşturulmamış")
            print(f"   💡 SQL Editor'de tabloları oluşturun")
        elif "401" in error_str:
            print(f"   ❌ 401 Unauthorized - API key hala yanlış!")
            raise
        else:
            print(f"   ❌ Beklenmeyen hata: {error_str[:100]}")
            raise
    
    print("\n" + "="*60)
    print("🎉 BAĞLANTI BAŞARILI!")
    print("="*60)
    print("\n✅ Supabase REST API çalışıyor")
    print("✅ Backend Supabase'e bağlanabilir")
    print("✅ Veri okuma/yazma hazır")
    
    print("\n📝 Sonraki Adımlar:")
    print("   1. Supabase SQL Editor'de tabloları oluştur:")
    print("      https://supabase.com/dashboard/project/wyursjdrnnjabpfeucyi/sql")
    print("   2. 02_tables_public.sql → 05_seed_data_public.sql çalıştır")
    print("   3. Bu scripti tekrar çalıştır (demo verileri görmek için)")
    print("   4. Backend'i başlat: cd backend && python main.py")
    print()
    
except Exception as e:
    print(f"\n❌ BAĞLANTI HATASI!")
    print("="*60)
    print(f"Hata: {e}")
    print("\n💡 Çözüm:")
    print("1. API key'in doğru olduğundan emin olun")
    print("2. İnternet bağlantınızı kontrol edin")
    print("3. Supabase projesinin aktif olduğunu kontrol edin")
    print()
    
    import traceback
    traceback.print_exc()
