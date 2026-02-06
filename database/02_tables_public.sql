-- ============================================
-- SIRAMATIK TABLOLAR (INTEGER ID VERSIYONU)
-- ============================================

CREATE SCHEMA IF NOT EXISTS siramatik;
SET search_path TO siramatik;

-- 1. FİRMALAR
CREATE TABLE firmalar (
    id SERIAL PRIMARY KEY, -- 1, 2, 3...
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

-- 2. SERVISLER
CREATE TABLE servisler (
    id SERIAL PRIMARY KEY,
    firma_id INTEGER NOT NULL REFERENCES firmalar(id) ON DELETE CASCADE,
    ad VARCHAR(100) NOT NULL,
    kod VARCHAR(10) NOT NULL,
    aciklama TEXT,
    aktif BOOLEAN DEFAULT true,
    olusturulma TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT unique_firma_kod UNIQUE(firma_id, kod),
    CONSTRAINT kod_buyuk_harf CHECK (kod = UPPER(kod))
);

-- 3. KUYRUKLAR
CREATE TABLE kuyruklar (
    id SERIAL PRIMARY KEY,
    servis_id INTEGER NOT NULL REFERENCES servisler(id) ON DELETE CASCADE,
    ad VARCHAR(100) NOT NULL,
    kod VARCHAR(10) NOT NULL,
    aciklama TEXT,
    oncelik INT DEFAULT 0,
    sira_limiti INT DEFAULT 100,
    aktif BOOLEAN DEFAULT true,
    olusturulma TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT unique_servis_kod UNIQUE(servis_id, kod),
    CONSTRAINT kod_buyuk_harf_kuyruk CHECK (kod = UPPER(kod))
);

-- 4. KULLANICILAR
CREATE TABLE kullanicilar (
    id SERIAL PRIMARY KEY,
    firma_id INTEGER NOT NULL REFERENCES firmalar(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    ad_soyad VARCHAR(255) NOT NULL,
    rol VARCHAR(50) DEFAULT 'staff',
    sifre_hash VARCHAR(255) NOT NULL,
    telefon VARCHAR(20),
    aktif BOOLEAN DEFAULT true,
    son_giris TIMESTAMPTZ,
    olusturulma TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT valid_rol CHECK (rol IN ('admin', 'staff', 'kiosk', 'screen', 'manager'))
);

-- 5. SIRALAR
CREATE TABLE siralar (
    id SERIAL PRIMARY KEY,
    kuyruk_id INTEGER NOT NULL REFERENCES kuyruklar(id) ON DELETE CASCADE,
    servis_id INTEGER NOT NULL REFERENCES servisler(id) ON DELETE CASCADE,
    firma_id INTEGER NOT NULL REFERENCES firmalar(id) ON DELETE CASCADE,
    numara VARCHAR(20) NOT NULL,
    durum VARCHAR(20) DEFAULT 'waiting', -- waiting, calling, serving...
    oncelik INT DEFAULT 0,
    cagiran_kullanici_id INTEGER REFERENCES kullanicilar(id),
    konum VARCHAR(10),
    notlar TEXT,
    olusturulma TIMESTAMPTZ DEFAULT NOW(),
    cagirilma TIMESTAMPTZ,
    tamamlanma TIMESTAMPTZ,
    
    CONSTRAINT valid_durum CHECK (durum IN ('waiting', 'calling', 'serving', 'completed', 'cancelled', 'no_show')),
    CONSTRAINT valid_oncelik CHECK (oncelik >= 0 AND oncelik <= 9)
);

-- 6. CİHAZLAR
CREATE TABLE cihazlar (
    id SERIAL PRIMARY KEY,
    firma_id INTEGER NOT NULL REFERENCES firmalar(id) ON DELETE CASCADE,
    servis_id INTEGER REFERENCES servisler(id) ON DELETE SET NULL,
    kuyruk_id INTEGER REFERENCES kuyruklar(id) ON DELETE SET NULL,
    ad VARCHAR(100) NOT NULL,
    mac_adresi VARCHAR(17) UNIQUE,
    tip VARCHAR(50) NOT NULL,
    konum VARCHAR(100),
    ayarlar JSONB DEFAULT '{}'::jsonb,
    son_gorunme TIMESTAMPTZ,
    aktif BOOLEAN DEFAULT true,
    olusturulma TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT valid_tip CHECK (tip IN ('button', 'kiosk', 'screen1', 'screen2', 'tablet', 'pc'))
);

-- 7. CİHAZ OLAYLARI
CREATE TABLE cihaz_olaylari (
    id SERIAL PRIMARY KEY,
    cihaz_id INTEGER NOT NULL REFERENCES cihazlar(id) ON DELETE CASCADE,
    olay_tipi VARCHAR(50) NOT NULL,
    veri JSONB,
    olusturulma TIMESTAMPTZ DEFAULT NOW()
);

-- 8. SİSTEM AYARLARI
CREATE TABLE sistem_ayarlari (
    anahtar VARCHAR(100) PRIMARY KEY,
    deger JSONB NOT NULL,
    aciklama TEXT,
    guncelleme TIMESTAMPTZ DEFAULT NOW()
);
