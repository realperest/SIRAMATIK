-- ============================================
-- SIRAMATIK TABLOLAR
-- Tüm tablolar siramatik schema'sı altında
-- Sektör-agnostik tasarım (hastane, banka, belediye vb. için uygun)
-- ============================================

-- 1. FİRMALAR (Multi-tenant için hazır)
CREATE TABLE siramatik.firmalar (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ad VARCHAR(255) NOT NULL,
    logo_url TEXT,
    ayarlar JSONB DEFAULT '{
        "calisma_saatleri": "08:00-17:00",
        "bilet_sablonu": "varsayilan",
        "dil": "tr",
        "renk_tema": "#667eea"
    }'::jsonb,
    olusturulma TIMESTAMPTZ DEFAULT NOW(),
    aktif BOOLEAN DEFAULT true
);

COMMENT ON TABLE siramatik.firmalar IS 'Firma/Kurum bilgileri - Multi-tenant yapı için';
COMMENT ON COLUMN siramatik.firmalar.ayarlar IS 'Firma özel ayarları (JSON)';

-- 2. SERVISLER (Hizmet noktaları: Hastane departmanı, banka gişesi, belediye birimi vb.)
CREATE TABLE siramatik.servisler (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firma_id UUID NOT NULL REFERENCES siramatik.firmalar(id) ON DELETE CASCADE,
    ad VARCHAR(100) NOT NULL,
    kod VARCHAR(10) NOT NULL, -- 'LAB', 'BANK', 'A' vb.
    aciklama TEXT,
    aktif BOOLEAN DEFAULT true,
    olusturulma TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT unique_firma_kod UNIQUE(firma_id, kod),
    CONSTRAINT kod_buyuk_harf CHECK (kod = UPPER(kod))
);

COMMENT ON TABLE siramatik.servisler IS 'Hizmet noktaları (departman, şube, birim vb.)';
COMMENT ON COLUMN siramatik.servisler.kod IS 'Servis kodu (LAB, BANK, A vb.)';

-- 3. KUYRUKLAR (Bir servis içinde birden fazla kuyruk olabilir)
-- Örnek: Laboratuvar servisi içinde "Kan Testi" ve "İdrar Testi" kuyrukları
CREATE TABLE siramatik.kuyruklar (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    servis_id UUID NOT NULL REFERENCES siramatik.servisler(id) ON DELETE CASCADE,
    ad VARCHAR(100) NOT NULL, -- 'Kan Testi', 'İdrar Testi', 'Normal İşlem', 'Hızlı İşlem'
    kod VARCHAR(10) NOT NULL, -- 'A', 'B', 'C' (sıra numarası öneki)
    aciklama TEXT,
    oncelik INT DEFAULT 0, -- 0: Normal, 1-9: Yüksek öncelik (VIP, acil vb.)
    sira_limiti INT DEFAULT 100,
    aktif BOOLEAN DEFAULT true,
    olusturulma TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT unique_servis_kod UNIQUE(servis_id, kod),
    CONSTRAINT kod_buyuk_harf_kuyruk CHECK (kod = UPPER(kod))
);

COMMENT ON TABLE siramatik.kuyruklar IS 'Kuyruk tipleri - Bir servis içinde birden fazla kuyruk olabilir';
COMMENT ON COLUMN siramatik.kuyruklar.kod IS 'Kuyruk kodu - sıra numarası öneki (A, B, C vb.)';
COMMENT ON COLUMN siramatik.kuyruklar.oncelik IS '0: Normal, 1-9: VIP/Öncelikli kuyruk';

-- 4. KULLANICILAR (Personel, Admin)
CREATE TABLE siramatik.kullanicilar (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firma_id UUID NOT NULL REFERENCES siramatik.firmalar(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    ad_soyad VARCHAR(255) NOT NULL,
    rol VARCHAR(50) DEFAULT 'staff', -- 'admin', 'staff', 'kiosk', 'screen'
    sifre_hash VARCHAR(255) NOT NULL,
    telefon VARCHAR(20),
    aktif BOOLEAN DEFAULT true,
    son_giris TIMESTAMPTZ,
    olusturulma TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT valid_rol CHECK (rol IN ('admin', 'staff', 'kiosk', 'screen', 'manager'))
);

COMMENT ON TABLE siramatik.kullanicilar IS 'Sistem kullanıcıları (personel, adminler)';

-- 5. SIRALAR (Sıra numaraları)
CREATE TABLE siramatik.siralar (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kuyruk_id UUID NOT NULL REFERENCES siramatik.kuyruklar(id) ON DELETE CASCADE,
    servis_id UUID NOT NULL REFERENCES siramatik.servisler(id) ON DELETE CASCADE,
    firma_id UUID NOT NULL REFERENCES siramatik.firmalar(id) ON DELETE CASCADE,
    numara VARCHAR(20) NOT NULL, -- 'A001', 'B042', 'VIP001'
    durum VARCHAR(20) DEFAULT 'waiting', -- 'waiting', 'calling', 'serving', 'completed', 'cancelled'
    oncelik INT DEFAULT 0, -- 0: Normal, 1-9: Yüksek öncelik (torpil/VIP)
    cagiran_kullanici_id UUID REFERENCES siramatik.kullanicilar(id),
    konum VARCHAR(10), -- Hangi konuma çağrıldı (örn: "3", "A5", "Gişe 2")
    notlar TEXT,
    olusturulma TIMESTAMPTZ DEFAULT NOW(),
    cagirilma TIMESTAMPTZ,
    tamamlanma TIMESTAMPTZ,
    
    CONSTRAINT valid_durum CHECK (durum IN ('waiting', 'calling', 'serving', 'completed', 'cancelled', 'no_show')),
    CONSTRAINT valid_oncelik CHECK (oncelik >= 0 AND oncelik <= 9)
);

COMMENT ON TABLE siramatik.siralar IS 'Sıra numaraları (kuyruk kayıtları)';
COMMENT ON COLUMN siramatik.siralar.durum IS 'Sıra durumu: waiting, calling, serving, completed, cancelled, no_show';
COMMENT ON COLUMN siramatik.siralar.oncelik IS '0: Normal, 1-9: VIP/Öncelikli (torpil sistemi)';
COMMENT ON COLUMN siramatik.siralar.konum IS 'Çağrıldığı konum (oda, gişe, masa vb.)';

-- 6. CİHAZLAR (ESP32 butonlar, tabletler, ekranlar)
CREATE TABLE siramatik.cihazlar (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firma_id UUID NOT NULL REFERENCES siramatik.firmalar(id) ON DELETE CASCADE,
    servis_id UUID REFERENCES siramatik.servisler(id) ON DELETE SET NULL,
    kuyruk_id UUID REFERENCES siramatik.kuyruklar(id) ON DELETE SET NULL,
    ad VARCHAR(100) NOT NULL, -- 'Kiosk 1', 'Screen Lobby', 'Button Room 3'
    mac_adresi VARCHAR(17) UNIQUE, -- AA:BB:CC:DD:EE:FF (ESP32 için)
    tip VARCHAR(50) NOT NULL, -- 'button', 'kiosk', 'screen1', 'screen2'
    konum VARCHAR(100), -- 'Entrance', 'Lobby', 'Room 3'
    ayarlar JSONB DEFAULT '{}'::jsonb,
    son_gorunme TIMESTAMPTZ,
    aktif BOOLEAN DEFAULT true,
    olusturulma TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT valid_tip CHECK (tip IN ('button', 'kiosk', 'screen1', 'screen2', 'tablet'))
);

COMMENT ON TABLE siramatik.cihazlar IS 'IoT cihazları ve ekranlar';
COMMENT ON COLUMN siramatik.cihazlar.tip IS 'Cihaz tipi: button, kiosk, screen1, screen2, tablet';
COMMENT ON COLUMN siramatik.cihazlar.kuyruk_id IS 'Cihaz belirli bir kuyruğa atanabilir (opsiyonel)';

-- 7. CİHAZ OLAYLARI (Log/Audit için)
CREATE TABLE siramatik.cihaz_olaylari (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cihaz_id UUID NOT NULL REFERENCES siramatik.cihazlar(id) ON DELETE CASCADE,
    olay_tipi VARCHAR(50) NOT NULL, -- 'button_pressed', 'connection_lost', 'restarted'
    veri JSONB,
    olusturulma TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE siramatik.cihaz_olaylari IS 'Cihaz aktivite logları';

-- 8. SİSTEM AYARLARI (Global ayarlar)
CREATE TABLE siramatik.sistem_ayarlari (
    anahtar VARCHAR(100) PRIMARY KEY,
    deger JSONB NOT NULL,
    aciklama TEXT,
    guncelleme TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE siramatik.sistem_ayarlari IS 'Sistem geneli ayarlar (key-value store)';
