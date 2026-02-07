
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "backend"))
from database import db

def reset_sira_func():
    print("Sıra numarası fonksiyonu NORMALE döndürülüyor...")
    
    sql = """
CREATE OR REPLACE FUNCTION siramatik.yeni_sira_numarasi(p_kuyruk_id INTEGER, p_oncelik INT DEFAULT 0)
RETURNS VARCHAR AS $$
DECLARE
    kuyruk_kodu VARCHAR(10);
    sonraki_numara INT;
    yeni_numara VARCHAR(20);
    onek VARCHAR(10);
BEGIN
    -- Kuyruk kodunu al
    SELECT kod INTO kuyruk_kodu 
    FROM siramatik.kuyruklar 
    WHERE id = p_kuyruk_id;
    
    IF kuyruk_kodu IS NULL THEN
        RAISE EXCEPTION 'Kuyruk bulunamadı: %', p_kuyruk_id;
    END IF;
    
    -- Öncelik varsa VIP
    IF p_oncelik > 0 THEN
        onek := 'V';
    ELSE
        onek := kuyruk_kodu;
    END IF;
    
    -- Sıradaki numarayı bul (COUNT(*) + 1 mantığı ile, artık atlama yok)
    -- Veya MAX mantığı ile devam edebiliriz ama basitlik için normali yapalım.
    SELECT COUNT(*) + 1 INTO sonraki_numara
    FROM siramatik.siralar
    WHERE kuyruk_id = p_kuyruk_id
    AND DATE(olusturulma) = CURRENT_DATE
    AND numara LIKE (onek || '%');
    
    -- Numarayı oluştur
    yeni_numara := onek || LPAD(sonraki_numara::TEXT, 3, '0');
    
    RETURN yeni_numara;
END;
$$ LANGUAGE plpgsql;
    """
    
    try:
        db.execute_query(sql)
        print("✅ Fonksiyon başarıyla normale döndü.")
    except Exception as e:
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    reset_sira_func()
