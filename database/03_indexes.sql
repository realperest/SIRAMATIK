-- ============================================
-- SIRAMATIK İNDEKSLER
-- Performans optimizasyonu için
-- ============================================

-- SIRALAR tablosu indeksleri
CREATE INDEX idx_sira_firma ON siramatik.siralar(firma_id);
CREATE INDEX idx_sira_servis ON siramatik.siralar(servis_id);
CREATE INDEX idx_sira_kuyruk ON siramatik.siralar(kuyruk_id);
CREATE INDEX idx_sira_durum ON siramatik.siralar(durum) WHERE durum IN ('waiting', 'calling');
CREATE INDEX idx_sira_olusturulma ON siramatik.siralar(olusturulma DESC);
CREATE INDEX idx_sira_cagirilma ON siramatik.siralar(cagirilma DESC) WHERE cagirilma IS NOT NULL;

-- Composite index: Bekleyen sıraları önceliğe göre hızlı getirmek için
CREATE INDEX idx_sira_waiting_priority ON siramatik.siralar(kuyruk_id, oncelik DESC, olusturulma ASC) 
    WHERE durum = 'waiting';

-- KUYRUKLAR tablosu indeksleri
CREATE INDEX idx_kuyruk_servis ON siramatik.kuyruklar(servis_id);
CREATE INDEX idx_kuyruk_aktif ON siramatik.kuyruklar(servis_id, aktif) WHERE aktif = true;
CREATE INDEX idx_kuyruk_oncelik ON siramatik.kuyruklar(oncelik DESC);

-- SERVISLER tablosu indeksleri
CREATE INDEX idx_servis_firma ON siramatik.servisler(firma_id);
CREATE INDEX idx_servis_aktif ON siramatik.servisler(firma_id, aktif) WHERE aktif = true;

-- KULLANICILAR tablosu indeksleri
CREATE INDEX idx_kullanici_firma ON siramatik.kullanicilar(firma_id);
CREATE INDEX idx_kullanici_email ON siramatik.kullanicilar(email);
CREATE INDEX idx_kullanici_rol ON siramatik.kullanicilar(firma_id, rol);

-- CİHAZLAR tablosu indeksleri
CREATE INDEX idx_cihaz_firma ON siramatik.cihazlar(firma_id);
CREATE INDEX idx_cihaz_servis ON siramatik.cihazlar(servis_id);
CREATE INDEX idx_cihaz_kuyruk ON siramatik.cihazlar(kuyruk_id);
CREATE INDEX idx_cihaz_tip ON siramatik.cihazlar(tip);
CREATE INDEX idx_cihaz_mac ON siramatik.cihazlar(mac_adresi) WHERE mac_adresi IS NOT NULL;

-- CİHAZ_OLAYLARI tablosu indeksleri
CREATE INDEX idx_olay_cihaz ON siramatik.cihaz_olaylari(cihaz_id);
CREATE INDEX idx_olay_tarih ON siramatik.cihaz_olaylari(olusturulma DESC);
CREATE INDEX idx_olay_tip ON siramatik.cihaz_olaylari(olay_tipi);
