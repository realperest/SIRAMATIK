"""
Backend Schema Test
Supabase'in hangi schema'yı kullandığını kontrol et
"""
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

print("🔍 Backend Schema Testi\n")

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Public schema'yı dene
    print("1️⃣ Public schema test ediliyor...")
    try:
        response = supabase.table('firmalar').select('*').limit(1).execute()
        print(f"   ✅ Public.firmalar okunabilir: {len(response.data)} kayıt")
    except Exception as e:
        print(f"   ❌ Public.firmalar okunamıyor: {str(e)[:80]}")
    
    # Siramatik schema'yı dene (çalışmayacak, REST API schema belirtmeyi desteklemiyor)
    print("\n2️⃣ Siramatik schema test ediliyor...")
    try:
        response = supabase.schema('siramatik').table('firmalar').select('*').limit(1).execute()
        print(f"   ✅ Siramatik.firmalar okunabilir: {len(response.data)} kayıt")
    except Exception as e:
        error_msg = str(e)
        if "schema" in error_msg.lower():
            print(f"   ❌ .schema() metodu desteklenmiyor")
        else:
            print(f"   ❌ Hata: {error_msg[:80]}")
    
    print("\n" + "="*60)
    print("📝 SONUÇ")
    print("="*60)
    print("\nSupabase Python client REST API kullanır ve")
    print("schema belirtmeyi desteklemez.")
    print("\n💡 Çözüm:")
    print("1. Supabase Dashboard > Settings > API")
    print("2. 'Exposed schemas' kısmına 'siramatik' ekle")
    print("3. 'db_schema' ayarını 'siramatik' yap")
    print()
    
except Exception as e:
    print(f"❌ Hata: {e}")
