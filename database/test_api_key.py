"""
Supabase API Key Test
Hangi key'in çalıştığını bulalım
"""
from supabase import create_client
import sys

SUPABASE_URL = "https://wyursjdrnnjabpfeucyi.supabase.co"

# Farklı key'leri deneyelim
keys_to_test = [
    ("Anon Key (Kısa)", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind5dXJzamRybm5qYWJwZmV1Y3lpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzg4NDI3NzcsImV4cCI6MjA1NDQxODc3N30.iqGPKpXVCJ9"),
]

print("="*60)
print("🔑 SUPABASE API KEY TEST")
print("="*60)

for key_name, key_value in keys_to_test:
    print(f"\n🧪 Test: {key_name}")
    print(f"   Key: {key_value[:40]}...")
    
    try:
        supabase = create_client(SUPABASE_URL, key_value)
        
        # Basit bir health check
        response = supabase.table('_supabase_migrations').select('*').limit(1).execute()
        
        print(f"   ✅ ÇALIŞIYOR!")
        print(f"   📊 Response: {response}")
        
    except Exception as e:
        error_str = str(e)
        if "401" in error_str:
            print(f"   ❌ 401 Unauthorized - Key geçersiz")
        elif "404" in error_str or "not found" in error_str.lower():
            print(f"   ⚠️  404 - Tablo yok (ama key çalışıyor olabilir)")
        elif "relation" in error_str.lower():
            print(f"   ✅ Key çalışıyor! (Tablo henüz yok)")
        else:
            print(f"   ❌ Hata: {error_str[:100]}")

print("\n" + "="*60)
print("\n💡 Çözüm:")
print("1. Supabase Dashboard > Settings > API")
print("2. 'anon' key'i kopyala")
print("3. backend/.env dosyasına yapıştır")
print()
