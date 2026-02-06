-- ============================================
-- SIRAMATIK DEMO VERİLERİ
-- Test ve geliştirme için örnek veriler
-- Örnek: Laboratuvar servisi (kan testi, idrar testi kuyrukları)
-- ============================================

-- 1. Demo Firma Oluştur
INSERT INTO firmalar (id, ad, logo_url, ayarlar) VALUES
(
    '11111111-1111-1111-1111-111111111111',
    'Demo Medical Center',
    'https://via.placeholder.com/200x80?text=Demo+Medical',
    '{
        "calisma_saatleri": "08:00-17:00",
        "bilet_sablonu": "varsayilan",
        "dil": "tr",
        "renk_tema": "#667eea",
        "sesli_anons": true,
        "sms_bildirimi": false
    }'::jsonb
);

-- 2. Servisler Ekle
INSERT INTO servisler (firma_id, ad, kod, aciklama) VALUES
('11111111-1111-1111-1111-111111111111', 'Laboratory', 'LAB', 'Medical laboratory service'),
('11111111-1111-1111-1111-111111111111', 'Registration', 'REG', 'Patient registration desk'),
('11111111-1111-1111-1111-111111111111', 'Pharmacy', 'PHR', 'Pharmacy service');

-- 3. Kuyruklar Ekle (Bir servis içinde birden fazla kuyruk)
DO $$
DECLARE
    lab_id UUID;
    reg_id UUID;
    phr_id UUID;
BEGIN
    SELECT id INTO lab_id FROM servisler WHERE kod = 'LAB';
    SELECT id INTO reg_id FROM servisler WHERE kod = 'REG';
    SELECT id INTO phr_id FROM servisler WHERE kod = 'PHR';
    
    -- Laboratuvar servisi altında 3 kuyruk
    INSERT INTO kuyruklar (servis_id, ad, kod, aciklama, oncelik) VALUES
    (lab_id, 'Blood Test', 'A', 'Blood sample collection queue', 0),
    (lab_id, 'Urine Test', 'B', 'Urine sample collection queue', 0),
    (lab_id, 'X-Ray', 'C', 'X-Ray imaging queue', 0);
    
    -- Kayıt servisi altında 2 kuyruk
    INSERT INTO kuyruklar (servis_id, ad, kod, aciklama, oncelik) VALUES
    (reg_id, 'New Patient', 'A', 'New patient registration', 0),
    (reg_id, 'Returning Patient', 'B', 'Returning patient check-in', 0);
    
    -- Eczane servisi altında 2 kuyruk (biri VIP)
    INSERT INTO kuyruklar (servis_id, ad, kod, aciklama, oncelik) VALUES
    (phr_id, 'Regular Queue', 'A', 'Standard pharmacy queue', 0),
    (phr_id, 'Priority Queue', 'V', 'VIP/Priority pharmacy queue', 5);
END $$;

-- 4. Kullanıcılar Ekle
-- Şifre: admin123 (bcrypt hash)
INSERT INTO kullanicilar (firma_id, email, ad_soyad, rol, sifre_hash) VALUES
(
    '11111111-1111-1111-1111-111111111111',
    'admin@demo.com',
    'Admin User',
    'admin',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ztpXFxVqNqe6'
),
(
    '11111111-1111-1111-1111-111111111111',
    'staff1@demo.com',
    'Lab Staff 1',
    'staff',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ztpXFxVqNqe6'
),
(
    '11111111-1111-1111-1111-111111111111',
    'staff2@demo.com',
    'Registration Staff',
    'staff',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ztpXFxVqNqe6'
);

-- 5. Cihazlar Ekle
DO $$
DECLARE
    lab_id UUID;
    lab_blood_queue UUID;
    lab_urine_queue UUID;
BEGIN
    SELECT id INTO lab_id FROM servisler WHERE kod = 'LAB';
    SELECT id INTO lab_blood_queue FROM kuyruklar WHERE kod = 'A' AND servis_id = lab_id;
    SELECT id INTO lab_urine_queue FROM kuyruklar WHERE kod = 'B' AND servis_id = lab_id;
    
    INSERT INTO cihazlar (firma_id, servis_id, kuyruk_id, ad, tip, konum) VALUES
    ('11111111-1111-1111-1111-111111111111', lab_id, NULL, 'Kiosk Entrance', 'kiosk', 'Main Entrance'),
    ('11111111-1111-1111-1111-111111111111', lab_id, NULL, 'Screen Lobby', 'screen1', 'Lobby'),
    ('11111111-1111-1111-1111-111111111111', lab_id, lab_blood_queue, 'Button Blood Test', 'button', 'Blood Test Room'),
    ('11111111-1111-1111-1111-111111111111', lab_id, lab_urine_queue, 'Button Urine Test', 'button', 'Urine Test Room');
END $$;

-- 6. Örnek Sıra Numaraları (Bugün için)
DO $$
DECLARE
    lab_blood_queue UUID;
    lab_urine_queue UUID;
    phr_regular_queue UUID;
    phr_vip_queue UUID;
BEGIN
    -- Kuyruk ID'lerini al
    SELECT k.id INTO lab_blood_queue 
    FROM kuyruklar k 
    JOIN servisler s ON k.servis_id = s.id 
    WHERE s.kod = 'LAB' AND k.kod = 'A';
    
    SELECT k.id INTO lab_urine_queue 
    FROM kuyruklar k 
    JOIN servisler s ON k.servis_id = s.id 
    WHERE s.kod = 'LAB' AND k.kod = 'B';
    
    SELECT k.id INTO phr_regular_queue 
    FROM kuyruklar k 
    JOIN servisler s ON k.servis_id = s.id 
    WHERE s.kod = 'PHR' AND k.kod = 'A';
    
    SELECT k.id INTO phr_vip_queue 
    FROM kuyruklar k 
    JOIN servisler s ON k.servis_id = s.id 
    WHERE s.kod = 'PHR' AND k.kod = 'V';
    
    -- Kan testi kuyruğu için 5 sıra (2 normal, 1 VIP)
    FOR i IN 1..5 LOOP
        INSERT INTO siralar (
            kuyruk_id, 
            servis_id,
            firma_id, 
            numara, 
            durum,
            oncelik,
            olusturulma
        ) VALUES (
            lab_blood_queue,
            (SELECT servis_id FROM kuyruklar WHERE id = lab_blood_queue),
            '11111111-1111-1111-1111-111111111111',
            CASE WHEN i = 3 THEN 'VIP001' ELSE 'A' || LPAD(i::TEXT, 3, '0') END,
            CASE 
                WHEN i <= 2 THEN 'completed'
                WHEN i = 3 THEN 'calling'
                ELSE 'waiting'
            END,
            CASE WHEN i = 3 THEN 5 ELSE 0 END,  -- 3. sıra VIP
            NOW() - (i || ' minutes')::INTERVAL
        );
    END LOOP;
    
    -- İdrar testi kuyruğu için 3 sıra
    FOR i IN 1..3 LOOP
        INSERT INTO siralar (
            kuyruk_id, 
            servis_id,
            firma_id, 
            numara, 
            durum,
            oncelik,
            olusturulma
        ) VALUES (
            lab_urine_queue,
            (SELECT servis_id FROM kuyruklar WHERE id = lab_urine_queue),
            '11111111-1111-1111-1111-111111111111',
            'B' || LPAD(i::TEXT, 3, '0'),
            CASE 
                WHEN i = 1 THEN 'calling'
                ELSE 'waiting'
            END,
            0,
            NOW() - (i * 2 || ' minutes')::INTERVAL
        );
    END LOOP;
    
    -- Eczane VIP kuyruğu için 2 sıra
    INSERT INTO siralar (kuyruk_id, servis_id, firma_id, numara, durum, oncelik) VALUES
    (phr_vip_queue, (SELECT servis_id FROM kuyruklar WHERE id = phr_vip_queue), '11111111-1111-1111-1111-111111111111', 'VIP001', 'waiting', 9),
    (phr_vip_queue, (SELECT servis_id FROM kuyruklar WHERE id = phr_vip_queue), '11111111-1111-1111-1111-111111111111', 'VIP002', 'waiting', 9);
    
END $$;

-- 7. Sistem Ayarları
INSERT INTO sistem_ayarlari (anahtar, deger, aciklama) VALUES
('varsayilan_tema', '{"primary": "#667eea", "secondary": "#764ba2"}'::jsonb, 'Varsayılan renk teması'),
('max_bekleyen_sira', '100'::jsonb, 'Kuyruk başına maksimum bekleyen sıra sayısı'),
('eski_veri_temizleme_gun', '180'::jsonb, 'Kaç gün sonra eski veriler silinsin'),
('sesli_anons_aktif', 'true'::jsonb, 'Sesli anons sistemi aktif mi?'),
('vip_oncelik_seviyesi', '5'::jsonb, 'VIP sıralar için varsayılan öncelik seviyesi (1-9)');

-- Başarı mesajı
DO $$
BEGIN
    RAISE NOTICE '✅ Demo veriler başarıyla eklendi!';
    RAISE NOTICE '📧 Admin Email: admin@demo.com';
    RAISE NOTICE '🔑 Şifre: admin123';
    RAISE NOTICE '';
    RAISE NOTICE '📊 Oluşturulan yapı:';
    RAISE NOTICE '  - 3 Servis (Laboratory, Registration, Pharmacy)';
    RAISE NOTICE '  - 7 Kuyruk (Kan testi, İdrar testi, X-Ray, vb.)';
    RAISE NOTICE '  - VIP/Öncelikli sıra sistemi aktif';
    RAISE NOTICE '';
    RAISE NOTICE '💡 Örnek: Laboratuvar servisi altında 3 ayrı kuyruk var:';
    RAISE NOTICE '    A: Kan Testi, B: İdrar Testi, C: X-Ray';
END $$;
