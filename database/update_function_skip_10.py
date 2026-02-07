
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "backend"))
from database import db

def update_sira_func():
    print("Sıra numarası fonksiyonu güncelleniyor (Her 10'da bir atlama)...")
    
    sql = """
CREATE OR REPLACE FUNCTION siramatik.yeni_sira_numarasi(p_kuyruk_id INTEGER, p_oncelik INT DEFAULT 0)
RETURNS VARCHAR AS $$
DECLARE
    kuyruk_kodu VARCHAR(10);
    sonraki_numara INT;
    yeni_numara VARCHAR(20);
    onek VARCHAR(10);
BEGIN
    -- Kuyruk kodunu al (örn: 'A')
    SELECT kod INTO kuyruk_kodu 
    FROM siramatik.kuyruklar 
    WHERE id = p_kuyruk_id;
    
    IF kuyruk_kodu IS NULL THEN
        RAISE EXCEPTION 'Kuyruk bulunamadı: %', p_kuyruk_id;
    END IF;
    
    -- Öncelikli sıra mı?
    IF p_oncelik > 0 THEN
        onek := 'VIP';
    ELSE
        onek := kuyruk_kodu;
    END IF;
    
    -- Bugün bu kuyrukta verilmiş en büyük numarayı bul (Regex ile sadece sayıları al)
    -- Veya basitçe, numara formatımız Harf+Rakam olduğu için substring ile alabiliriz.
    -- Örn: A001 -> 001 -> 1
    -- VIP001 -> 001 -> 1 (Bu durumda VIP ile normal kuyruk numaraları çakışabilir mi? Evet!)
    -- Sizin yapıda VIP ve Normal aynı kuyrukta mı? Evet.
    -- Ama VIP prefix'i farklı.
    -- Sorun şu: A010 mu atlanacak yoksa VIP010 mu?
    -- Hile: "Her 10 numarada bir numara atlasın" dediğiniz sanırım GENEL NUMARA.
    
    -- En son verilen numarayı bulmak için prefix'e göre filtreleyelim
    SELECT COALESCE(MAX(REGEXP_REPLACE(numara, '[^0-9]', '', 'g')::INT), 0) + 1 INTO sonraki_numara
    FROM siramatik.siralar
    WHERE kuyruk_id = p_kuyruk_id
    AND DATE(olusturulma) = CURRENT_DATE
    AND numara LIKE (onek || '%');
    
    -- HİLE: Eğer 10'un katıysa bir atla (Boş kalsın)
    IF sonraki_numara % 10 = 0 THEN
        sonraki_numara := sonraki_numara + 1;
    END IF;
    
    -- Numarayı oluştur (örn: 'A001' veya 'VIP001')
    yeni_numara := onek || LPAD(sonraki_numara::TEXT, 3, '0');
    
    RETURN yeni_numara;
END;
$$ LANGUAGE plpgsql;
    """
    
    try:
        db.execute_query(sql)
        print("✅ Fonksiyon başarıyla güncellendi.")
    except Exception as e:
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    update_sira_func()
