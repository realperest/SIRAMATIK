"""
Admin Şifresini Sıfırla (Bcrypt ile)
Basit bcrypt kütüphanesi kullanarak güncelle
"""
import bcrypt
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

# Database bağlantısı - Siramatik schema
DB_URL = "postgresql://postgres.wyursjdrnnjabpfeucyi:qk4SEnyhu3NUk2@aws-1-eu-central-1.pooler.supabase.com:6543/postgres"

print("🔑 Şifre Sıfırlama Aracı v2\n")

try:
    print("1️⃣ Yeni hash oluşturuluyor...")
    password = b"admin123"
    
    # Yeni bir salt ile hash oluştur
    hashed = bcrypt.hashpw(password, bcrypt.gensalt())
    hashed_str = hashed.decode('utf-8')
    
    print(f"   Şifre: admin123")
    print(f"   Hash: {hashed_str}")
    
    print("\n2️⃣ Veritabanı güncelleniyor...")
    engine = create_engine(DB_URL, echo=False, connect_args={"options": "-c search_path=siramatik,public"})
    
    with Session(engine) as session:
        email = "admin@demo.com"
        
        # Güncelle
        result = session.execute(text("""
            UPDATE siramatik.kullanicilar 
            SET sifre_hash = :hash 
            WHERE email = :email
        """), {"hash": hashed_str, "email": email})
        
        session.commit()
        
        if result.rowcount > 0:
            print(f"   ✅ {email} şifresi güncellendi!")
        else:
            print(f"   ⚠️  Kullanıcı bulunamadı!")
            
    print("\n✅ Tamamlandı! Şimdi giriş yapmayı deneyin.")

except Exception as e:
    print(f"❌ Hata: {e}")
