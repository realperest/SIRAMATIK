"""
Eski kayıtların timestamp alanlarına +3 saat ekleyen tek seferlik script.

NOT:
- Bu script üretim veritabanında ÇALIŞIR; ikinci kez çalıştırmamanız gerekir.
- Sadece siramatik şemasındaki ilgili timestamp kolonlarına +3 saat ekler.
"""

from sqlalchemy import text
from database import engine, db


def main():
    # Güvenlik için önce kullanıcıya hangi offset'in kullanılacağını göster
    offset = db.get_timezone_offset()
    print(f"[INFO] Sistem timezone_offset = {offset}. Eski kayıtlara +{offset} saat eklenecek.")

    if offset != 3:
        print(
            "[WARN] timezone_offset şu anda 3 değil. "
            "Bu script sadece UTC → UTC+3 dönüşümü için tasarlandı."
        )

    with engine.begin() as conn:
        # 1) siralar tablosu
        print("[INFO] siramatik.siralar için timestamp alanları güncelleniyor...")
        conn.execute(
            text(
                """
                UPDATE siramatik.siralar
                SET olusturulma = olusturulma + INTERVAL '3 hours'
                WHERE olusturulma IS NOT NULL;

                UPDATE siramatik.siralar
                SET cagirilma = cagirilma + INTERVAL '3 hours'
                WHERE cagirilma IS NOT NULL;

                UPDATE siramatik.siralar
                SET tamamlanma = tamamlanma + INTERVAL '3 hours'
                WHERE tamamlanma IS NOT NULL;

                UPDATE siramatik.siralar
                SET islem_baslangic = islem_baslangic + INTERVAL '3 hours'
                WHERE islem_baslangic IS NOT NULL;
                """
            )
        )

        # 2) cihazlar tablosu
        print("[INFO] siramatik.cihazlar için timestamp alanları güncelleniyor...")
        conn.execute(
            text(
                """
                UPDATE siramatik.cihazlar
                SET son_gorulen = son_gorulen + INTERVAL '3 hours'
                WHERE son_gorulen IS NOT NULL;

                UPDATE siramatik.cihazlar
                SET olusturulma = olusturulma + INTERVAL '3 hours'
                WHERE olusturulma IS NOT NULL;

                UPDATE siramatik.cihazlar
                SET guncelleme = guncelleme + INTERVAL '3 hours'
                WHERE guncelleme IS NOT NULL;
                """
            )
        )

        # 3) memnuniyet_anketleri tablosu
        print("[INFO] siramatik.memnuniyet_anketleri için timestamp alanları güncelleniyor...")
        conn.execute(
            text(
                """
                UPDATE siramatik.memnuniyet_anketleri
                SET anket_tarihi = anket_tarihi + INTERVAL '3 hours'
                WHERE anket_tarihi IS NOT NULL;
                """
            )
        )

        # 4) Diğer tablo örnekleri gerekiyorsa buraya eklenebilir

    print("[OK] Eski timestamp kayıtlarına +3 saat eklendi. Bu script'i bir daha ÇALIŞTIRMAYIN.")


if __name__ == "__main__":
    main()

