-- ============================================
-- SIRAMATIK İNDEKSLER
-- Performans optimizasyonu için
-- ============================================

-- SIRALAR tablosu indeksleri
CREATE INDEX idx_sira_firma ON siralar(firma_id);
CREATE INDEX idx_sira_servis ON siralar(servis_id);
CREATE INDEX idx_sira_kuyruk ON siralar(kuyruk_id);
CREATE INDEX idx_sira_durum ON siralar(durum) WHERE durum IN ('waiting', 'calling');
CREATE INDEX idx_sira_olusturulma ON siralar(olusturulma DESC);
CREATE INDEX idx_sira_cagirilma ON siralar(cagirilma DESC) WHERE cagirilma IS NOT NULL;

-- Composite index: Bekleyen sıraları önceliğe göre hızlı getirmek için
CREATE INDEX idx_sira_waiting_priority ON siralar(kuyruk_id, oncelik DESC, olusturulma ASC) 
    WHERE durum = 'waiting';

-- KUYRUKLAR tablosu indeksleri
CREATE INDEX idx_kuyruk_servis ON kuyruklar(servis_id);
CREATE INDEX idx_kuyruk_aktif ON kuyruklar(servis_id, aktif) WHERE aktif = true;
CREATE INDEX idx_kuyruk_oncelik ON kuyruklar(oncelik DESC);

-- SERVISLER tablosu indeksleri
CREATE INDEX idx_servis_firma ON servisler(firma_id);
CREATE INDEX idx_servis_aktif ON servisler(firma_id, aktif) WHERE aktif = true;

-- KULLANICILAR tablosu indeksleri
CREATE INDEX idx_kullanici_firma ON kullanicilar(firma_id);
CREATE INDEX idx_kullanici_email ON kullanicilar(email);
CREATE INDEX idx_kullanici_rol ON kullanicilar(firma_id, rol);

-- CİHAZLAR tablosu indeksleri
CREATE INDEX idx_cihaz_firma ON cihazlar(firma_id);
CREATE INDEX idx_cihaz_servis ON cihazlar(servis_id);
CREATE INDEX idx_cihaz_kuyruk ON cihazlar(kuyruk_id);
CREATE INDEX idx_cihaz_tip ON cihazlar(tip);
CREATE INDEX idx_cihaz_mac ON cihazlar(mac_adresi) WHERE mac_adresi IS NOT NULL;

-- CİHAZ_OLAYLARI tablosu indeksleri
CREATE INDEX idx_olay_cihaz ON cihaz_olaylari(cihaz_id);
CREATE INDEX idx_olay_tarih ON cihaz_olaylari(olusturulma DESC);
CREATE INDEX idx_olay_tip ON cihaz_olaylari(olay_tipi);
