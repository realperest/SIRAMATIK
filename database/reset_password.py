"""
Admin Şifresini Sıfırla
Geçerli hash ile admin kullanıcısını güncelle
"""
from passlib.context import CryptContext
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

# Şifreleme bağlamı
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

# Database bağlantısı
DB_URL = "postgresql://postgres.wyursjdrnnjabpfeucyi:qk4SEnyhu3NUk2@aws-1-eu-central-1.pooler.supabase.com:6543/postgres"

print("🔑 Şifre Sıfırlama Aracı\n")

try:
    print("1️⃣ Yeni hash oluşturuluyor...")
    yeni_sifre = "admin123"
    yeni_hash = get_password_hash(yeni_sifre)
    print(f"   Yeni şifre: {yeni_sifre}")
    print(f"   Hash: {yeni_hash[:20]}...")
    
    print("\n2️⃣ Veritabanı güncelleniyor...")
    engine = create_engine(DB_URL, echo=False, connect_args={"options": "-c search_path=siramatik,public"})
    
    with Session(engine) as session:
        # Admin kullanıcısını bul ve güncelle
        email = "admin@demo.com"
        
        # Kullanıcı var mı kontrol et
        result = session.execute(text("SELECT id FROM siramatik.kullanicilar WHERE email = :email"), {"email": email})
        user = result.fetchone()
        
        if user:
            # Güncelle
            session.execute(text("""
                UPDATE siramatik.kullanicilar 
                SET sifre_hash = :hash 
                WHERE email = :email
            """), {"hash": yeni_hash, "email": email})
            session.commit()
            print(f"   ✅ {email} şifresi güncellendi!")
        else:
            print(f"   ⚠️  kullanıcı bulunamadı!")
            
            # Kullanıcı yoksa oluştur
            print("   ➕ Kullanıcı yeniden oluşturuluyor...")
            session.execute(text("""
                INSERT INTO siramatik.kullanicilar (firma_id, email, ad_soyad, rol, sifre_hash)
                VALUES (
                    '11111111-1111-1111-1111-111111111111',
                    :email,
                    'Admin User',
                    'admin',
                    :hash
                )
            """), {"email": email, "hash": yeni_hash})
            session.commit()
            print(f"   ✅ {email} oluşturuldu!")

    print("\n✅ İŞLEM TAMAMLANDI!")
    print("   Lütfen şimdi giriş yapmayı deneyin.")

except Exception as e:
    print(f"❌ Hata: {e}")
