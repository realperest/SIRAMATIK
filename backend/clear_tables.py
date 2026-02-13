"""
Sıralar ve Cihazlar tablolarını temizleme scripti

DİKKAT: Bu script tüm sıra ve cihaz kayıtlarını SİLER!
Sadece test için kullanılmalıdır.
"""

from database import Database
from sqlalchemy import text

db = Database()

print("=" * 60)
print("TABLO TEMİZLEME SCRIPTİ")
print("=" * 60)
print("\n⚠️  DİKKAT: Bu script tüm sıra ve cihaz kayıtlarını SİLECEK!")
print("   Devam etmek için 'EVET' yazın: ", end="")

confirmation = input().strip().upper()

if confirmation != "EVET":
    print("\n❌ İşlem iptal edildi.")
    exit(0)

print("\n[1] Sıralar tablosu temizleniyor...")
try:
    with db.engine.begin() as conn:
        result = conn.execute(text("DELETE FROM siramatik.siralar"))
        print(f"    ✓ {result.rowcount} sıra kaydı silindi.")
except Exception as e:
    print(f"    ✗ Hata: {e}")

print("\n[2] Cihazlar tablosu temizleniyor...")
try:
    with db.engine.begin() as conn:
        result = conn.execute(text("DELETE FROM siramatik.cihazlar"))
        print(f"    ✓ {result.rowcount} cihaz kaydı silindi.")
except Exception as e:
    print(f"    ✗ Hata: {e}")

print("\n[3] Sıra numarası sayaçları sıfırlanıyor...")
try:
    with db.engine.begin() as conn:
        # Tüm kuyruklar için sayaçları sıfırla
        conn.execute(text("""
            UPDATE siramatik.kuyruklar
            SET son_numara = 0
            WHERE son_numara IS NOT NULL
        """))
        print("    ✓ Sayaçlar sıfırlandı.")
except Exception as e:
    print(f"    ✗ Hata: {e}")

print("\n" + "=" * 60)
print("✅ Temizleme tamamlandı!")
print("=" * 60)
print("\nArtık yeni kayıtlar ekleyebilirsiniz.")
print("Yeni kayıtlar yerel saat ile doğru şekilde kaydedilecektir.")
