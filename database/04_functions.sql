-- ============================================
-- SIRAMATIK FONKSİYONLAR
-- Otomatik işlemler için
-- Sektör-agnostik tasarım + Kuyruk sistemi
-- ============================================

-- 1. Otomatik sıra numarası üretme (kuyruk bazlı)
CREATE OR REPLACE FUNCTION siramatik.yeni_sira_numarasi(p_kuyruk_id UUID, p_oncelik INT DEFAULT 0)
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
    
    -- Bugün bu kuyrukta kaç numara verilmiş?
    SELECT COUNT(*) + 1 INTO sonraki_numara
    FROM siramatik.siralar
    WHERE kuyruk_id = p_kuyruk_id
    AND DATE(olusturulma) = CURRENT_DATE;
    
    -- Numarayı oluştur (örn: 'A001' veya 'VIP001')
    yeni_numara := onek || LPAD(sonraki_numara::TEXT, 3, '0');
    
    RETURN yeni_numara;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION siramatik.yeni_sira_numarasi IS 'Kuyruk için otomatik sıra numarası üretir. Öncelikli sıralar VIP öneki alır.';

-- 2. Bekleyen sıra sayısını getir (önceliğe göre)
CREATE OR REPLACE FUNCTION siramatik.bekleyen_sira_sayisi(p_kuyruk_id UUID, p_oncelik INT DEFAULT NULL)
RETURNS INT AS $$
BEGIN
    IF p_oncelik IS NULL THEN
        -- Tüm bekleyenler
        RETURN (
            SELECT COUNT(*)::INT
            FROM siramatik.siralar
            WHERE kuyruk_id = p_kuyruk_id
            AND durum = 'waiting'
        );
    ELSE
        -- Belirli öncelik seviyesi
        RETURN (
            SELECT COUNT(*)::INT
            FROM siramatik.siralar
            WHERE kuyruk_id = p_kuyruk_id
            AND durum = 'waiting'
            AND oncelik = p_oncelik
        );
    END IF;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION siramatik.bekleyen_sira_sayisi IS 'Kuyruktaki bekleyen sayısını döndürür. Öncelik belirtilirse sadece o önceliği sayar.';

-- 3. Sıradaki kişiyi getir (öncelik sırasına göre)
CREATE OR REPLACE FUNCTION siramatik.siradaki_kisi(p_kuyruk_id UUID)
RETURNS TABLE (
    sira_id UUID,
    numara VARCHAR,
    oncelik INT,
    olusturulma TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        id,
        siralar.numara,
        siralar.oncelik,
        siralar.olusturulma
    FROM siramatik.siralar
    WHERE kuyruk_id = p_kuyruk_id
    AND durum = 'waiting'
    ORDER BY 
        siralar.oncelik DESC,  -- Önce yüksek öncelikli
        siralar.olusturulma ASC  -- Sonra eski tarihli
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION siramatik.siradaki_kisi IS 'Kuyruktaki sıradaki kişiyi getirir (öncelik > zaman sırası)';

-- 4. Ortalama bekleme süresi (dakika)
CREATE OR REPLACE FUNCTION siramatik.ortalama_bekleme_suresi(p_kuyruk_id UUID, p_gun_sayisi INT DEFAULT 7)
RETURNS INT AS $$
DECLARE
    ort_saniye NUMERIC;
BEGIN
    SELECT AVG(EXTRACT(EPOCH FROM (cagirilma - olusturulma)))
    INTO ort_saniye
    FROM siramatik.siralar
    WHERE kuyruk_id = p_kuyruk_id
    AND durum IN ('calling', 'completed')
    AND olusturulma > NOW() - (p_gun_sayisi || ' days')::INTERVAL
    AND cagirilma IS NOT NULL;
    
    RETURN COALESCE(ROUND(ort_saniye / 60), 0)::INT;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION siramatik.ortalama_bekleme_suresi IS 'Son N gündeki ortalama bekleme süresini dakika olarak döndürür';

-- 5. Günlük kuyruk istatistikleri
CREATE OR REPLACE FUNCTION siramatik.gunluk_istatistikler(p_firma_id UUID, p_tarih DATE DEFAULT CURRENT_DATE)
RETURNS TABLE (
    servis_ad VARCHAR,
    kuyruk_ad VARCHAR,
    toplam_sira BIGINT,
    vip_sira BIGINT,
    tamamlanan BIGINT,
    iptal BIGINT,
    ortalama_bekleme_dk INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.ad,
        k.ad,
        COUNT(q.id),
        COUNT(q.id) FILTER (WHERE q.oncelik > 0),
        COUNT(q.id) FILTER (WHERE q.durum = 'completed'),
        COUNT(q.id) FILTER (WHERE q.durum IN ('cancelled', 'no_show')),
        COALESCE(
            ROUND(AVG(EXTRACT(EPOCH FROM (q.cagirilma - q.olusturulma)) / 60))::INT,
            0
        )
    FROM siramatik.servisler s
    LEFT JOIN siramatik.kuyruklar k ON s.id = k.servis_id
    LEFT JOIN siramatik.siralar q ON k.id = q.kuyruk_id 
        AND DATE(q.olusturulma) = p_tarih
    WHERE s.firma_id = p_firma_id
    GROUP BY s.ad, k.ad
    ORDER BY s.ad, k.ad;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION siramatik.gunluk_istatistikler IS 'Belirli bir gün için kuyruk bazlı istatistikler (VIP sayısı dahil)';

-- 6. Eski sıraları temizle (GDPR/KVKK uyumu)
CREATE OR REPLACE FUNCTION siramatik.eski_siralari_temizle(p_gun_sayisi INT DEFAULT 180)
RETURNS INT AS $$
DECLARE
    silinen_sayisi INT;
BEGIN
    DELETE FROM siramatik.siralar
    WHERE olusturulma < NOW() - (p_gun_sayisi || ' days')::INTERVAL
    AND durum IN ('completed', 'cancelled', 'no_show');
    
    GET DIAGNOSTICS silinen_sayisi = ROW_COUNT;
    
    RETURN silinen_sayisi;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION siramatik.eski_siralari_temizle IS 'Belirtilen günden eski tamamlanmış sıraları siler (varsayılan: 180 gün)';
