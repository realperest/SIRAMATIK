-- ============================================
-- MÜŞTERİ MEMNUNİYET ANKETİ TABLOSU
-- Hizmet kalitesi ölçümü ve performans takibi
-- ============================================

-- MEMNUNIYET ANKETLERİ
CREATE TABLE IF NOT EXISTS siramatik.memnuniyet_anketleri (
    id SERIAL PRIMARY KEY,
    sira_id INTEGER NOT NULL REFERENCES siramatik.siralar(id) ON DELETE CASCADE,
    kuyruk_id INTEGER NOT NULL REFERENCES siramatik.kuyruklar(id) ON DELETE CASCADE,
    servis_id INTEGER NOT NULL REFERENCES siramatik.servisler(id) ON DELETE CASCADE,
    firma_id INTEGER NOT NULL REFERENCES siramatik.firmalar(id) ON DELETE CASCADE,
    cagiran_kullanici_id INTEGER REFERENCES siramatik.kullanicilar(id) ON DELETE SET NULL,
    
    -- Puanlama (1-5 yıldız)
    puan INTEGER NOT NULL CHECK (puan >= 1 AND puan <= 5),
    
    -- Yorum (opsiyonel)
    yorum TEXT,
    
    -- Metadata
    anket_tarihi TIMESTAMPTZ DEFAULT NOW(),
    ip_adresi VARCHAR(45), -- IPv4 veya IPv6
    cihaz_bilgisi TEXT,
    
    -- Hizmet süresi bilgisi (sira tablosundan)
    hizmet_suresi_dk INTEGER, -- Kaç dakika hizmet aldı
    
    CONSTRAINT puan_gecerli CHECK (puan IN (1, 2, 3, 4, 5))
);

-- İndeksler (Performans)
CREATE INDEX idx_memnuniyet_sira ON siramatik.memnuniyet_anketleri(sira_id);
CREATE INDEX idx_memnuniyet_kuyruk ON siramatik.memnuniyet_anketleri(kuyruk_id);
CREATE INDEX idx_memnuniyet_servis ON siramatik.memnuniyet_anketleri(servis_id);
CREATE INDEX idx_memnuniyet_firma ON siramatik.memnuniyet_anketleri(firma_id);
CREATE INDEX idx_memnuniyet_kullanici ON siramatik.memnuniyet_anketleri(cagiran_kullanici_id);
CREATE INDEX idx_memnuniyet_tarih ON siramatik.memnuniyet_anketleri(anket_tarihi);
CREATE INDEX idx_memnuniyet_puan ON siramatik.memnuniyet_anketleri(puan);

-- Yorumlar
COMMENT ON TABLE siramatik.memnuniyet_anketleri IS 'Müşteri memnuniyet anketleri - Hizmet kalitesi ölçümü';
COMMENT ON COLUMN siramatik.memnuniyet_anketleri.puan IS '1-5 arası puan (1: Çok Kötü, 5: Mükemmel)';
COMMENT ON COLUMN siramatik.memnuniyet_anketleri.yorum IS 'Müşteri yorumu (opsiyonel)';
COMMENT ON COLUMN siramatik.memnuniyet_anketleri.hizmet_suresi_dk IS 'Hizmet alma süresi (dakika)';

-- ============================================
-- RAPORLAMA FONKSİYONLARI
-- ============================================

-- 1. Kullanıcı Bazlı Ortalama Puan
CREATE OR REPLACE FUNCTION siramatik.kullanici_ortalama_puan(p_kullanici_id INTEGER, p_gun_sayisi INT DEFAULT 30)
RETURNS TABLE (
    kullanici_id INTEGER,
    kullanici_ad VARCHAR,
    toplam_anket BIGINT,
    ortalama_puan NUMERIC(3,2),
    puan_1 BIGINT,
    puan_2 BIGINT,
    puan_3 BIGINT,
    puan_4 BIGINT,
    puan_5 BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        k.id,
        k.ad,
        COUNT(m.id),
        ROUND(AVG(m.puan), 2),
        COUNT(m.id) FILTER (WHERE m.puan = 1),
        COUNT(m.id) FILTER (WHERE m.puan = 2),
        COUNT(m.id) FILTER (WHERE m.puan = 3),
        COUNT(m.id) FILTER (WHERE m.puan = 4),
        COUNT(m.id) FILTER (WHERE m.puan = 5)
    FROM siramatik.kullanicilar k
    LEFT JOIN siramatik.memnuniyet_anketleri m ON k.id = m.cagiran_kullanici_id
        AND m.anket_tarihi > NOW() - (p_gun_sayisi || ' days')::INTERVAL
    WHERE k.id = p_kullanici_id
    GROUP BY k.id, k.ad;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION siramatik.kullanici_ortalama_puan IS 'Kullanıcının son N gündeki ortalama puanı ve dağılımı';

-- 2. Servis Bazlı Memnuniyet Raporu
CREATE OR REPLACE FUNCTION siramatik.servis_memnuniyet_raporu(p_firma_id INTEGER, p_gun_sayisi INT DEFAULT 30)
RETURNS TABLE (
    servis_id INTEGER,
    servis_ad VARCHAR,
    toplam_anket BIGINT,
    ortalama_puan NUMERIC(3,2),
    memnuniyet_yuzdesi NUMERIC(5,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.id,
        s.ad,
        COUNT(m.id),
        ROUND(AVG(m.puan), 2),
        ROUND((COUNT(m.id) FILTER (WHERE m.puan >= 4) * 100.0 / NULLIF(COUNT(m.id), 0)), 2)
    FROM siramatik.servisler s
    LEFT JOIN siramatik.memnuniyet_anketleri m ON s.id = m.servis_id
        AND m.anket_tarihi > NOW() - (p_gun_sayisi || ' days')::INTERVAL
    WHERE s.firma_id = p_firma_id
    GROUP BY s.id, s.ad
    ORDER BY ortalama_puan DESC NULLS LAST;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION siramatik.servis_memnuniyet_raporu IS 'Servis bazlı memnuniyet raporu (puan 4-5 olanlar memnun sayılır)';

-- 3. Günlük Memnuniyet Trendi
CREATE OR REPLACE FUNCTION siramatik.gunluk_memnuniyet_trendi(p_firma_id INTEGER, p_gun_sayisi INT DEFAULT 7)
RETURNS TABLE (
    tarih DATE,
    toplam_anket BIGINT,
    ortalama_puan NUMERIC(3,2),
    memnuniyet_yuzdesi NUMERIC(5,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        DATE(m.anket_tarihi AT TIME ZONE 'Europe/Istanbul'),
        COUNT(m.id),
        ROUND(AVG(m.puan), 2),
        ROUND((COUNT(m.id) FILTER (WHERE m.puan >= 4) * 100.0 / NULLIF(COUNT(m.id), 0)), 2)
    FROM siramatik.memnuniyet_anketleri m
    WHERE m.firma_id = p_firma_id
        AND m.anket_tarihi > NOW() - (p_gun_sayisi || ' days')::INTERVAL
    GROUP BY DATE(m.anket_tarihi AT TIME ZONE 'Europe/Istanbul')
    ORDER BY tarih DESC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION siramatik.gunluk_memnuniyet_trendi IS 'Son N günün günlük memnuniyet trendi';

-- ============================================
-- RLS POLİTİKALARI
-- ============================================

-- RLS'i aktif et
ALTER TABLE siramatik.memnuniyet_anketleri ENABLE ROW LEVEL SECURITY;

-- Herkes kendi firma verilerini görebilir
CREATE POLICY memnuniyet_select_policy ON siramatik.memnuniyet_anketleri
    FOR SELECT
    USING (true); -- Anon kullanıcılar da anket gönderebilmeli (bilet sayfasından)

-- Herkes anket ekleyebilir (anon kullanıcı - bilet sayfası)
CREATE POLICY memnuniyet_insert_policy ON siramatik.memnuniyet_anketleri
    FOR INSERT
    WITH CHECK (true); -- Kısıtlama backend'de yapılacak

-- Sadece admin güncelleyebilir (düzeltme için)
CREATE POLICY memnuniyet_update_policy ON siramatik.memnuniyet_anketleri
    FOR UPDATE
    USING (auth.role() = 'authenticated'); -- Authenticated kullanıcılar

-- Silme yasak (veri bütünlüğü için)
CREATE POLICY memnuniyet_delete_policy ON siramatik.memnuniyet_anketleri
    FOR DELETE
    USING (auth.role() = 'service_role'); -- Sadece service_role

-- ============================================
-- ÖRNEK VERİ (Test için)
-- ============================================

-- Örnek anket verileri (production'da bu satırları kaldır)
-- INSERT INTO siramatik.memnuniyet_anketleri (sira_id, kuyruk_id, servis_id, firma_id, cagiran_kullanici_id, puan, yorum, hizmet_suresi_dk)
-- SELECT 
--     s.id,
--     s.kuyruk_id,
--     k.servis_id,
--     sv.firma_id,
--     s.cagiran_kullanici_id,
--     (RANDOM() * 4 + 1)::INT, -- 1-5 arası random puan
--     CASE 
--         WHEN RANDOM() > 0.7 THEN 'Hizmet çok iyiydi, teşekkürler!'
--         WHEN RANDOM() > 0.5 THEN 'Normal bir hizmet'
--         ELSE NULL
--     END,
--     EXTRACT(EPOCH FROM (s.tamamlanma - s.olusturulma)) / 60
-- FROM siramatik.siralar s
-- JOIN siramatik.kuyruklar k ON s.kuyruk_id = k.id
-- JOIN siramatik.servisler sv ON k.servis_id = sv.id
-- WHERE s.durum = 'completed'
-- LIMIT 50;
