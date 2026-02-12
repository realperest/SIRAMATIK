#!/usr/bin/env python3
"""
Son 3 ay içinde tamamlanmış 1000 adet dummy sıra kaydı ekler.
- Her kullanıcıya 20–200 arası rastgele dağıtılır (toplam 1000).
- Kayıtlar: durum='completed', olusturulma/cagirilma/tamamlanma son 3 ay içinde rastgele,
  çeşitli kuyruklar ve cagiran_kullanici_id atanmış.

Kullanım (proje kökünden):
  python backend/seed_completed_siralar.py
"""
import sys
import os
import random
from datetime import datetime, timedelta, timezone

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
from backend.database import Database


def main():
    db = Database()
    # Kullanıcılar (çağıran olacak)
    users = db.execute_query("SELECT id FROM siramatik.kullanicilar WHERE aktif = true")
    if not users:
        print("[HATA] Aktif kullanıcı bulunamadı.")
        return
    user_ids = [u["id"] for u in users]

    # Kuyruklar (servis + firma ile)
    queues = db.execute_query("""
        SELECT k.id AS kuyruk_id, k.servis_id, k.kod, s.firma_id
        FROM siramatik.kuyruklar k
        JOIN siramatik.servisler s ON s.id = k.servis_id
        WHERE k.aktif = true
    """)
    if not queues:
        print("[HATA] Kuyruk bulunamadı.")
        return

    # Her kullanıcıya 20–200 arası dağıt (toplam 1000)
    n_total = 1000
    n_users = len(user_ids)
    min_per_user, max_per_user = 20, 200
    if n_users * min_per_user > n_total:
        print(f"[HATA] En az {n_total // max_per_user} kullanıcı gerekir (her biri en fazla {max_per_user} kayıt). Şu an: {n_users}")
        return
    if n_users * max_per_user < n_total:
        print(f"[HATA] Toplam {n_total} kayıt için kullanıcı başına en fazla {max_per_user} ile en az {n_total // n_users} gerekir.")
        return

    # Önce herkese min_per_user ver, kalanı rastgele dağıt (max_per_user aşmayacak şekilde)
    counts = [min_per_user] * n_users
    remaining = n_total - min_per_user * n_users
    while remaining > 0:
        i = random.randint(0, n_users - 1)
        if counts[i] < max_per_user:
            counts[i] += 1
            remaining -= 1
    random.shuffle(counts)

    # Zaman aralığı: son 3 ay (UTC)
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=90)
    delta_seconds = 90 * 24 * 3600

    # 1000 kayıt için satır verileri üret
    rows = []
    for u_idx, user_id in enumerate(user_ids):
        n = counts[u_idx]
        for _ in range(n):
            q = random.choice(queues)
            kod = (q.get("kod") or "X")
            numara = f"{kod}{random.randint(1000, 9999)}"
            r = random.random()
            olusturulma = start + timedelta(seconds=int(r * delta_seconds))
            cagirilma = olusturulma + timedelta(minutes=random.randint(1, 30))
            tamamlanma = cagirilma + timedelta(minutes=random.randint(2, 15))
            rows.append({
                "kuyruk_id": q["kuyruk_id"],
                "servis_id": q["servis_id"],
                "firma_id": q["firma_id"],
                "numara": numara,
                "cagiran_kullanici_id": user_id,
                "olusturulma": olusturulma.strftime("%Y-%m-%d %H:%M:%S"),
                "cagirilma": cagirilma.strftime("%Y-%m-%d %H:%M:%S"),
                "tamamlanma": tamamlanma.strftime("%Y-%m-%d %H:%M:%S"),
            })

    from sqlalchemy import text
    from sqlalchemy.orm import Session

    BATCH = 100
    with Session(db.engine) as session:
        for i in range(0, len(rows), BATCH):
            batch = rows[i : i + BATCH]
            values = ", ".join(
                f"(:kuyruk_id_{j}, :servis_id_{j}, :firma_id_{j}, :numara_{j}, 'completed', 0, :cagiran_kullanici_id_{j}, "
                f"CAST(:olusturulma_{j} AS timestamptz), CAST(:cagirilma_{j} AS timestamptz), CAST(:tamamlanma_{j} AS timestamptz))"
                for j in range(len(batch))
            )
            params = {}
            for j, row in enumerate(batch):
                params[f"kuyruk_id_{j}"] = row["kuyruk_id"]
                params[f"servis_id_{j}"] = row["servis_id"]
                params[f"firma_id_{j}"] = row["firma_id"]
                params[f"numara_{j}"] = row["numara"]
                params[f"cagiran_kullanici_id_{j}"] = row["cagiran_kullanici_id"]
                params[f"olusturulma_{j}"] = row["olusturulma"]
                params[f"cagirilma_{j}"] = row["cagirilma"]
                params[f"tamamlanma_{j}"] = row["tamamlanma"]
            session.execute(
                text(f"""
                    INSERT INTO siramatik.siralar
                    (kuyruk_id, servis_id, firma_id, numara, durum, oncelik, cagiran_kullanici_id, olusturulma, cagirilma, tamamlanma)
                    VALUES {values}
                """),
                params,
            )
        session.commit()
    inserted = len(rows)

    print(f"[OK] Toplam {inserted} adet tamamlanmış sıra kaydı eklendi (son 3 ay, çeşitli kullanıcılar).")
    for u_idx, user_id in enumerate(user_ids):
        print(f"  Kullanıcı {user_id}: {counts[u_idx]} kayıt.")


if __name__ == "__main__":
    main()
