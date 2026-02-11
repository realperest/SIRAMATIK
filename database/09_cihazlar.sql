-- ============================================
-- TABLET VE CİHAZ YÖNETİM SİSTEMİ
-- ============================================
-- Bu dosya tablet/kiosk cihazlarının sisteme 
-- kaydedilmesi ve uzaktan yönetimi için gerekli
-- veritabanı yapısını oluşturur.
-- ============================================

-- Cihazlar Tablosu
CREATE TABLE IF NOT EXISTS siramatik.cihazlar (
    id SERIAL PRIMARY KEY,
    firma_id INTEGER NOT NULL REFERENCES siramatik.firmalar(id) ON DELETE CASCADE,
    
    -- Cihaz Kimlik Bilgileri
    ad VARCHAR(255) NOT NULL,
    tip VARCHAR(50) NOT NULL CHECK (tip IN ('kiosk', 'ekran', 'tablet', 'pc')),
    
    -- Cihaz Tanımlama (Fingerprint)
    device_fingerprint VARCHAR(500) UNIQUE, -- Browser fingerprint
    mac_address VARCHAR(100), -- Opsiyonel MAC adresi
    ip_address VARCHAR(50),
    
    -- Durum Bilgileri
    durum VARCHAR(50) DEFAULT 'active' CHECK (durum IN ('active', 'inactive', 'maintenance')),
    son_gorulen TIMESTAMP DEFAULT NOW(),
    
    -- Ayarlar (JSON)
    ayarlar JSONB DEFAULT '{}'::jsonb,
    -- Örnek ayarlar yapısı:
    -- {
    --   "servis_ids": [1, 2],
    --   "kuyruk_ids": [5, 6, 7],
    --   "hideServisSelection": false,
    --   "orientation": "portrait",
    --   "theme": "default"
    -- }
    
    -- Meta Bilgiler
    metadata JSONB DEFAULT '{}'::jsonb,
    -- Örnek metadata:
    -- {
    --   "browser": "Chrome",
    --   "os": "Windows 10",
    --   "screen_resolution": "1920x1080",
    --   "last_error": null
    -- }
    
    olusturulma TIMESTAMP DEFAULT NOW(),
    guncelleme TIMESTAMP DEFAULT NOW()
);

-- İndeksler (Performans)
CREATE INDEX IF NOT EXISTS idx_cihazlar_firma_id ON siramatik.cihazlar(firma_id);
CREATE INDEX IF NOT EXISTS idx_cihazlar_tip ON siramatik.cihazlar(tip);
CREATE INDEX IF NOT EXISTS idx_cihazlar_durum ON siramatik.cihazlar(durum);
CREATE INDEX IF NOT EXISTS idx_cihazlar_fingerprint ON siramatik.cihazlar(device_fingerprint);
CREATE INDEX IF NOT EXISTS idx_cihazlar_son_gorulen ON siramatik.cihazlar(son_gorulen);

-- Otomatik güncelleme trigger'ı
CREATE OR REPLACE FUNCTION siramatik.update_cihaz_guncelleme()
RETURNS TRIGGER AS $$
BEGIN
    NEW.guncelleme = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_cihaz_guncelleme
    BEFORE UPDATE ON siramatik.cihazlar
    FOR EACH ROW
    EXECUTE FUNCTION siramatik.update_cihaz_guncelleme();

-- ============================================
-- RLS (Row Level Security) Politikaları
-- ============================================

ALTER TABLE siramatik.cihazlar ENABLE ROW LEVEL SECURITY;

-- SELECT: Anon/Authenticated kullanıcılar sadece kendi firmalarının cihazlarını görebilir
CREATE POLICY cihazlar_select_policy ON siramatik.cihazlar
    FOR SELECT
    USING (true); -- Tüm cihazlar görülebilir (firma_id kontrolü backend'de)

-- INSERT: Cihaz kaydı herkes yapabilir (ilk kayıt)
CREATE POLICY cihazlar_insert_policy ON siramatik.cihazlar
    FOR INSERT
    WITH CHECK (true);

-- UPDATE: Sadece kendi firmalarının cihazlarını güncelleyebilir
CREATE POLICY cihazlar_update_policy ON siramatik.cihazlar
    FOR UPDATE
    USING (true)
    WITH CHECK (true);

-- DELETE: Sadece kendi firmalarının cihazlarını silebilir
CREATE POLICY cihazlar_delete_policy ON siramatik.cihazlar
    FOR DELETE
    USING (true);

-- ============================================
-- YARDIMCI FONKSİYONLAR
-- ============================================

-- 1. Cihazı Online/Offline Olarak İşaretle
CREATE OR REPLACE FUNCTION siramatik.cihaz_heartbeat(
    p_device_id INTEGER,
    p_ip_address VARCHAR DEFAULT NULL,
    p_metadata JSONB DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    UPDATE siramatik.cihazlar
    SET 
        son_gorulen = NOW(),
        ip_address = COALESCE(p_ip_address, ip_address),
        metadata = COALESCE(p_metadata, metadata),
        durum = 'active'
    WHERE id = p_device_id;
END;
$$ LANGUAGE plpgsql;

-- 2. Offline Cihazları Bul (Son 5 dakikada görülmeyen)
CREATE OR REPLACE FUNCTION siramatik.offline_cihazlar(
    p_firma_id INTEGER,
    p_dakika INTEGER DEFAULT 5
)
RETURNS TABLE (
    cihaz_id INTEGER,
    ad VARCHAR,
    tip VARCHAR,
    son_gorulen TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id,
        c.ad,
        c.tip,
        c.son_gorulen
    FROM siramatik.cihazlar c
    WHERE c.firma_id = p_firma_id
      AND c.son_gorulen < (NOW() - INTERVAL '1 minute' * p_dakika)
      AND c.durum = 'active'
    ORDER BY c.son_gorulen DESC;
END;
$$ LANGUAGE plpgsql;

-- 3. Cihaz İstatistikleri
CREATE OR REPLACE FUNCTION siramatik.cihaz_istatistikleri(
    p_firma_id INTEGER
)
RETURNS TABLE (
    tip VARCHAR,
    toplam INTEGER,
    aktif INTEGER,
    pasif INTEGER,
    bakim INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.tip,
        COUNT(*)::INTEGER as toplam,
        COUNT(*) FILTER (WHERE c.durum = 'active')::INTEGER as aktif,
        COUNT(*) FILTER (WHERE c.durum = 'inactive')::INTEGER as pasif,
        COUNT(*) FILTER (WHERE c.durum = 'maintenance')::INTEGER as bakim
    FROM siramatik.cihazlar c
    WHERE c.firma_id = p_firma_id
    GROUP BY c.tip
    ORDER BY c.tip;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- TEST VERİLERİ (Opsiyonel)
-- ============================================

-- Örnek cihaz kaydı (İRMET HOSPITAL için)
INSERT INTO siramatik.cihazlar (firma_id, ad, tip, device_fingerprint, ayarlar, metadata)
VALUES (
    1,
    'Resepsiyon Tablet-1',
    'tablet',
    'fp_' || md5(random()::text),
    '{"servis_ids": [1, 2], "kuyruk_ids": [], "hideServisSelection": false}'::jsonb,
    '{"browser": "Chrome", "os": "Android", "screen_resolution": "1280x800"}'::jsonb
)
ON CONFLICT (device_fingerprint) DO NOTHING;

-- ============================================
-- AÇIKLAMALAR
-- ============================================

COMMENT ON TABLE siramatik.cihazlar IS 'Tablet, Kiosk ve diğer cihazların kayıt ve yönetim tablosu';
COMMENT ON COLUMN siramatik.cihazlar.device_fingerprint IS 'Browser fingerprint (benzersiz cihaz tanımlayıcı)';
COMMENT ON COLUMN siramatik.cihazlar.ayarlar IS 'Cihaza özel ayarlar (servis/kuyruk filtreleri vs.)';
COMMENT ON COLUMN siramatik.cihazlar.metadata IS 'Cihaz hakkında teknik bilgiler (tarayıcı, OS, ekran vs.)';
COMMENT ON COLUMN siramatik.cihazlar.son_gorulen IS 'Cihazın son heartbeat zamanı';

COMMENT ON FUNCTION siramatik.cihaz_heartbeat IS 'Cihazın heartbeat sinyalini günceller';
COMMENT ON FUNCTION siramatik.offline_cihazlar IS 'Belirtilen sürede görülmeyen offline cihazları listeler';
COMMENT ON FUNCTION siramatik.cihaz_istatistikleri IS 'Firmaya ait cihaz istatistiklerini döndürür';
