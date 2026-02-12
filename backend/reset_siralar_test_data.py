#!/usr/bin/env python3
"""
siralar tablosunu tamamen temizleyip test verisi doldurur:
- Tüm siralar silinir (TRUNCATE).
- Her aktif kuyruktan 5'er kayıt eklenir.
- Hepsi durum='waiting', olusturulma = son 10 dakika içinde rastgele.
- cagiran_kullanici_id, cagirilma, tamamlanma hep NULL kalır.

Kullanım (proje kökünden):
  python backend/reset_siralar_test_data.py
"""
import sys
import os
# Proje kökünü path'e ekle (script backend/ içinden veya kökten çalıştırılsın)
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
from backend.database import Database

def main():
    db = Database()
    engine = db.engine
    from sqlalchemy import text
    from sqlalchemy.orm import Session

    with Session(engine) as session:
        # 1) Tabloyu tamamen boşalt (tüm kayıtlar gider, cagiran_kullanici_id dahil)
        session.execute(text("TRUNCATE TABLE siramatik.siralar RESTART IDENTITY CASCADE"))
        session.commit()
        print("[OK] siramatik.siralar tablosu tamamen temizlendi.")

        # 2) Her kuyruktan 5'er sıra: son 10 dakika içinde rastgele olusturulma, hepsi waiting
        session.execute(text("""
            INSERT INTO siramatik.siralar (kuyruk_id, servis_id, firma_id, numara, durum, oncelik, olusturulma)
            SELECT
                k.id,
                k.servis_id,
                s.firma_id,
                k.kod || LPAD(g.n::text, 3, '0'),
                'waiting',
                0,
                NOW() - (random() * interval '10 minutes')
            FROM siramatik.kuyruklar k
            JOIN siramatik.servisler s ON s.id = k.servis_id
            CROSS JOIN generate_series(1, 5) AS g(n)
            WHERE k.aktif = true
        """))
        session.commit()
        print("[OK] Her kuyruktan 5'er bekleyen sıra eklendi (olusturulma: son 10 dk içinde rastgele).")

    # Kontrol
    rows = db.execute_query("SELECT COUNT(*) AS n FROM siramatik.siralar")
    n = rows[0]["n"] if rows else 0
    waiting = db.execute_query("SELECT COUNT(*) AS n FROM siramatik.siralar WHERE durum = 'waiting'")
    w = waiting[0]["n"] if waiting else 0
    called = db.execute_query("SELECT COUNT(*) AS n FROM siramatik.siralar WHERE cagiran_kullanici_id IS NOT NULL")
    c = called[0]["n"] if called else 0
    print(f"[Kontrol] Toplam: {n}, bekleyen: {w}, çağrılmış (cagiran_kullanici_id dolu): {c}")
    if c != 0:
        print("[UYARI] Beklenmedik: çağrılmış kayıt var. Tabloyu tekrar kontrol edin.")
    else:
        print("Tabloda artık sadece test verisi var; cagiran_kullanici_id hep NULL olmalı.")

if __name__ == "__main__":
    main()
