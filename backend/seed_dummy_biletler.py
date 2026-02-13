#!/usr/bin/env python3
"""
Son 30 dakika içinde oluşturulmuş gibi görünecek şekilde, çeşitli kuyruklarda
kuyruk başına 10'ar dummy bilet ekler. Mevcut verileri silmez.

Kullanım (proje kökünden):
  python backend/seed_dummy_biletler.py
"""
import sys
import os
import re

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from backend.database import Database


def max_numeric_suffix(db: Database, kuyruk_id: int, kod: str) -> int:
    """Bu kuyruktaki numara kayıtlarından (örn. K001, K022) en büyük sayıyı döndürür."""
    rows = db.execute_query(
        "SELECT numara FROM siramatik.siralar WHERE kuyruk_id = :kid AND numara LIKE :pattern",
        {"kid": kuyruk_id, "pattern": str(kod or "").strip() + "%"}
    )
    max_val = 0
    for r in (rows or []):
        numara = (r.get("numara") or "")
        suffix = re.sub(r"^[A-Za-z]*", "", numara)
        if suffix.isdigit():
            max_val = max(max_val, int(suffix))
    return max_val


def main():
    db = Database()
    queues = db.execute_query("""
        SELECT k.id AS kuyruk_id, k.kod, k.servis_id, s.firma_id
        FROM siramatik.kuyruklar k
        JOIN siramatik.servisler s ON s.id = k.servis_id
        WHERE k.aktif = true
        ORDER BY k.id
    """)
    if not queues:
        print("[UYARI] Aktif kuyruk bulunamadı.")
        return

    total_added = 0
    for q in queues:
        kuyruk_id = q["kuyruk_id"]
        kod = (q.get("kod") or "X").strip()
        servis_id = q["servis_id"]
        firma_id = q["firma_id"]
        base = max_numeric_suffix(db, kuyruk_id, kod)
        # 10 yeni numara: base+1 .. base+10
        db.execute_query("""
            INSERT INTO siramatik.siralar (kuyruk_id, servis_id, firma_id, numara, durum, oncelik, olusturulma)
            SELECT
                :kuyruk_id,
                :servis_id,
                :firma_id,
                :kod || LPAD((:base + g.n)::text, 3, '0'),
                'waiting',
                0,
                NOW() - (random() * interval '30 minutes')
            FROM generate_series(1, 10) AS g(n)
        """, {
            "kuyruk_id": kuyruk_id,
            "servis_id": servis_id,
            "firma_id": firma_id,
            "kod": kod,
            "base": base,
        })
        total_added += 10
        print(f"  {kod} (kuyruk_id={kuyruk_id}): {kod}{base+1:03d} .. {kod}{base+10:03d} eklendi.")

    print(f"\n[OK] Toplam {total_added} dummy bilet eklendi (son 30 dk içinde rastgele olusturulma).")
    print(f"     Kuyruk sayısı: {len(queues)}, kuyruk başına 10 bilet.")


if __name__ == "__main__":
    main()
