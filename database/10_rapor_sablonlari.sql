-- ============================================
-- RAPOR ŞABLONLARI TABLOSU
-- AG-Grid ve diğer raporlar için kullanıcı şablonlarını saklar
-- ============================================

CREATE TABLE IF NOT EXISTS siramatik.rapor_sablonlari (
    id SERIAL PRIMARY KEY,
    firma_id INTEGER NOT NULL REFERENCES siramatik.firmalar(id) ON DELETE CASCADE,
    kullanici_id INTEGER REFERENCES siramatik.kullanicilar(id) ON DELETE CASCADE,
    ad VARCHAR(255) NOT NULL,
    aciklama TEXT,
    rapor_tipi VARCHAR(50) DEFAULT 'ag_grid', -- 'ag_grid', 'pivot', 'custom'
    ayarlar JSONB NOT NULL DEFAULT '{}'::jsonb,
    varsayilan BOOLEAN DEFAULT FALSE,
    olusturulma TIMESTAMPTZ DEFAULT NOW(),
    guncelleme TIMESTAMPTZ DEFAULT NOW(),
    
    -- Aynı firma içinde aynı isimde şablon olmasın
    CONSTRAINT unique_firma_sablon_ad UNIQUE(firma_id, ad)
);

-- İndeksler
CREATE INDEX IF NOT EXISTS idx_rapor_sablonlari_firma_id ON siramatik.rapor_sablonlari(firma_id);
CREATE INDEX IF NOT EXISTS idx_rapor_sablonlari_kullanici_id ON siramatik.rapor_sablonlari(kullanici_id);
CREATE INDEX IF NOT EXISTS idx_rapor_sablonlari_rapor_tipi ON siramatik.rapor_sablonlari(rapor_tipi);

-- Row Level Security
ALTER TABLE siramatik.rapor_sablonlari ENABLE ROW LEVEL SECURITY;

-- Politikalar
DROP POLICY IF EXISTS rapor_sablonlari_select_policy ON siramatik.rapor_sablonlari;
CREATE POLICY rapor_sablonlari_select_policy ON siramatik.rapor_sablonlari
    FOR SELECT USING (true);

DROP POLICY IF EXISTS rapor_sablonlari_insert_policy ON siramatik.rapor_sablonlari;
CREATE POLICY rapor_sablonlari_insert_policy ON siramatik.rapor_sablonlari
    FOR INSERT WITH CHECK (true);

DROP POLICY IF EXISTS rapor_sablonlari_update_policy ON siramatik.rapor_sablonlari;
CREATE POLICY rapor_sablonlari_update_policy ON siramatik.rapor_sablonlari
    FOR UPDATE USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS rapor_sablonlari_delete_policy ON siramatik.rapor_sablonlari;
CREATE POLICY rapor_sablonlari_delete_policy ON siramatik.rapor_sablonlari
    FOR DELETE USING (true);

-- Açıklamalar
COMMENT ON TABLE siramatik.rapor_sablonlari IS 'Kullanıcı rapor şablonları (AG-Grid vb.)';
COMMENT ON COLUMN siramatik.rapor_sablonlari.ayarlar IS 'JSON formatında şablon ayarları (columnState, filterModel, pivotMode vb.)';
COMMENT ON COLUMN siramatik.rapor_sablonlari.varsayilan IS 'Bu şablon firmadaki tüm kullanıcılar için varsayılan mı?';
