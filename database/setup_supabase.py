"""
Sıramatik - Supabase Tablo Oluşturma
YAPLUS projesinden esinlenildi - SQLAlchemy ile direkt bağlantı
"""
from sqlalchemy import create_engine, text
import os

# YAPLUS'tan öğrendiğimiz: Pooler URL de çalışıyor!
# Direkt DB: IPv4 gerektirir, Pooler: IPv4 uyumlu
# Not: YAPLUS aws-1 kullanıyor, biz aws-0 - bu fark önemli olabilir
DB_URL = "postgresql://postgres.wyursjdrnnjabpfeucyi:qk4SEnyhu3NUk2@aws-1-eu-central-1.pooler.supabase.com:6543/postgres"

# SQL dosyalarının yolu
DB_DIR = os.path.dirname(__file__)

def read_sql_file(filename):
    """SQL dosyasını oku"""
    filepath = os.path.join(DB_DIR, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def execute_sql_file(engine, filename, description):
    """SQL dosyasını çalıştır"""
    print(f"\n{'='*60}")
    print(f"📝 {description}")
    print(f"{'='*60}")
    
    try:
        sql = read_sql_file(filename)
        
        with engine.connect() as conn:
            # SQL'i çalıştır
            conn.execute(text(sql))
            conn.commit()
        
        print(f"✅ Başarılı!")
        return True
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False

def main():
    """Ana kurulum fonksiyonu"""
    print("\n" + "="*60)
    print("🚀 SIRAMATIK - SUPABASE OTOMATIK KURULUM")
    print("   (YAPLUS yöntemi ile)")
    print("="*60)
    print(f"📍 Database: db.wyursjdrnnjabpfeucyi.supabase.co")
    print()
    
    try:
        # SQLAlchemy engine oluştur
        print("1️⃣ Database engine oluşturuluyor...")
        engine = create_engine(DB_URL, echo=False)
        print("   ✅ Engine oluşturuldu")
        
        # Bağlantıyı test et
        print("\n2️⃣ Bağlantı test ediliyor...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT NOW();"))
            server_time = result.fetchone()[0]
            print(f"   ✅ Bağlantı başarılı!")
            print(f"   ⏰ Sunucu zamanı: {server_time}")
        
        # SQL dosyalarını sırayla çalıştır (SIRAMATIK SCHEMA)
        sql_files = [
            ("01_schema.sql", "Schema Oluşturuluyor"),
            ("02_tables.sql", "Tablolar Oluşturuluyor (siramatik schema - 8 tablo)"),
            ("03_indexes.sql", "İndeksler Ekleniyor"),
            ("04_functions.sql", "Fonksiyonlar Ekleniyor (6 fonksiyon)"),
            ("05_seed_data.sql", "Demo Veriler Ekleniyor"),
        ]
        
        success_count = 0
        
        for filename, description in sql_files:
            if execute_sql_file(engine, filename, description):
                success_count += 1
            else:
                print(f"\n⚠️  {filename} çalıştırılamadı!")
                user_input = input("Devam etmek istiyor musunuz? (e/h): ")
                if user_input.lower() != 'e':
                    break
        
        print("\n" + "="*60)
        if success_count == len(sql_files):
            print(f"🎉 KURULUM BAŞARIYLA TAMAMLANDI!")
        else:
            print(f"⚠️  Kısmi Kurulum ({success_count}/{len(sql_files)} başarılı)")
        print("="*60)
        
        if success_count > 0:
            print("\n📊 Oluşturulan Yapı:")
            print("  ✅ public schema")
            if success_count >= 1:
                print("  ✅ 8 Tablo (firmalar, servisler, kuyruklar, siralar, vb.)")
            if success_count >= 2:
                print("  ✅ Performans indeksleri")
            if success_count >= 3:
                print("  ✅ 6 Fonksiyon (VIP sıra üretme, istatistik, vb.)")
            if success_count >= 4:
                print("  ✅ Demo veriler (1 firma, 3 servis, 7 kuyruk)")
            
            print("\n🔐 Demo Giriş:")
            print("  📧 Email: admin@demo.com")
            print("  🔑 Şifre: admin123")
            
            print("\n🚀 Sonraki Adımlar:")
            print("  1. cd D:\\KODLAMALAR\\GITHUB\\SIRAMATIK\\backend")
            print("  2. python main.py")
            print("  3. Tarayıcıda aç: http://localhost:8000/docs")
        print()
        
    except Exception as e:
        print(f"\n❌ BAĞLANTI HATASI!")
        print("="*60)
        print(f"Hata: {e}")
        print("\n💡 Olası Nedenler:")
        print("1. IPv6 ağındasınız (direkt bağlantı IPv4 gerektirir)")
        print("2. Şifre yanlış")
        print("3. Firewall/VPN engelliyor")
        print()
        
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # SQLAlchemy kurulu mu kontrol et
    try:
        from sqlalchemy import create_engine, text
    except ImportError:
        print("\n❌ SQLAlchemy kurulu değil!")
        print("Lütfen şu komutu çalıştırın:")
        print("  pip install sqlalchemy")
        exit(1)
    
    main()
