# 🗄️ MEMNUNİYET ANKETİ TABLOSU KURULUMU

## ⚠️ ÖNEMLİ: Database'de tablo YOK!

Şu anda `siramatik.memnuniyet_anketleri` tablosu Supabase'de yok. Önce oluşturmalısın.

---

## 📋 ADIM ADIM KURULUM

### **1. Supabase Dashboard'a Git**

```
https://supabase.com/dashboard
```

1. Projeyi seç
2. Sol menüden **"SQL Editor"** bölümüne tıkla

---

### **2. Migration Dosyasını Aç**

Proje klasöründe:
```
database/08_memnuniyet.sql
```

**VEYA** aşağıdaki SQL kodunu kullan:

---

### **3. SQL Kodunu Kopyala ve Çalıştır**

```sql
-- ============================================
-- MÜŞTERİ MEMNUNİYET ANKETİ TABLOSU
-- ============================================

-- TABLOYU OLUŞTUR
CREATE TABLE IF NOT EXISTS siramatik.memnuniyet_anketleri (
    id SERIAL PRIMARY KEY,
    sira_id INTEGER NOT NULL REFERENCES siramatik.siralar(id) ON DELETE CASCADE,
    kuyruk_id INTEGER NOT NULL REFERENCES siramatik.kuyruklar(id) ON DELETE CASCADE,
    servis_id INTEGER REFERENCES siramatik.servisler(id) ON DELETE CASCADE,
    firma_id INTEGER NOT NULL REFERENCES siramatik.firmalar(id) ON DELETE CASCADE,
    cagiran_kullanici_id INTEGER REFERENCES siramatik.kullanicilar(id) ON DELETE SET NULL,
    
    -- Puanlama (1-5 yıldız)
    puan INTEGER NOT NULL CHECK (puan >= 1 AND puan <= 5),
    
    -- Yorum (opsiyonel)
    yorum TEXT,
    
    -- Metadata
    anket_tarihi TIMESTAMPTZ DEFAULT NOW(),
    ip_adresi VARCHAR(45),
    cihaz_bilgisi TEXT,
    hizmet_suresi_dk INTEGER,
    
    CONSTRAINT puan_gecerli CHECK (puan IN (1, 2, 3, 4, 5))
);

-- İNDEKSLER
CREATE INDEX IF NOT EXISTS idx_memnuniyet_sira ON siramatik.memnuniyet_anketleri(sira_id);
CREATE INDEX IF NOT EXISTS idx_memnuniyet_kuyruk ON siramatik.memnuniyet_anketleri(kuyruk_id);
CREATE INDEX IF NOT EXISTS idx_memnuniyet_servis ON siramatik.memnuniyet_anketleri(servis_id);
CREATE INDEX IF NOT EXISTS idx_memnuniyet_firma ON siramatik.memnuniyet_anketleri(firma_id);
CREATE INDEX IF NOT EXISTS idx_memnuniyet_kullanici ON siramatik.memnuniyet_anketleri(cagiran_kullanici_id);
CREATE INDEX IF NOT EXISTS idx_memnuniyet_tarih ON siramatik.memnuniyet_anketleri(anket_tarihi);
CREATE INDEX IF NOT EXISTS idx_memnuniyet_puan ON siramatik.memnuniyet_anketleri(puan);

-- YORUMLAR
COMMENT ON TABLE siramatik.memnuniyet_anketleri IS 'Müşteri memnuniyet anketleri';
COMMENT ON COLUMN siramatik.memnuniyet_anketleri.puan IS '1-5 arası puan (1: Çok Kötü, 5: Mükemmel)';

-- RLS POLİTİKALARI
ALTER TABLE siramatik.memnuniyet_anketleri ENABLE ROW LEVEL SECURITY;

-- Herkes okuyabilir
CREATE POLICY IF NOT EXISTS memnuniyet_select_policy ON siramatik.memnuniyet_anketleri
    FOR SELECT
    USING (true);

-- Herkes ekleyebilir (anon kullanıcı - bilet sayfası)
CREATE POLICY IF NOT EXISTS memnuniyet_insert_policy ON siramatik.memnuniyet_anketleri
    FOR INSERT
    WITH CHECK (true);

-- Sadece authenticated güncelleyebilir
CREATE POLICY IF NOT EXISTS memnuniyet_update_policy ON siramatik.memnuniyet_anketleri
    FOR UPDATE
    USING (auth.role() = 'authenticated');

-- Silme yasak
CREATE POLICY IF NOT EXISTS memnuniyet_delete_policy ON siramatik.memnuniyet_anketleri
    FOR DELETE
    USING (auth.role() = 'service_role');
```

---

### **4. "RUN" Butonuna Bas**

Sağ alttaki yeşil **"RUN"** butonuna tıkla.

**Sonuç:**
```
Success. No rows returned
```

---

### **5. Tabloyu Kontrol Et**

#### **Yöntem 1: Table Editor**
1. Sol menüden **"Table Editor"** seç
2. **Schema: siramatik** seç
3. **memnuniyet_anketleri** tablosunu göreceksin

#### **Yöntem 2: SQL Query**
```sql
SELECT * FROM siramatik.memnuniyet_anketleri;
```

Şu sütunları göreceksin:
- `id`
- `sira_id`
- `kuyruk_id`
- `servis_id`
- `firma_id`
- `cagiran_kullanici_id`
- `puan`
- `yorum`
- `anket_tarihi`
- `ip_adresi`
- `cihaz_bilgisi`
- `hizmet_suresi_dk`

---

## ✅ DOĞRULAMA

Tablo oluştuktan sonra test et:

### **Test SQL:**
```sql
INSERT INTO siramatik.memnuniyet_anketleri 
(sira_id, kuyruk_id, servis_id, firma_id, puan, yorum)
VALUES 
(1, 1, 1, 1, 5, 'Test anket');

SELECT * FROM siramatik.memnuniyet_anketleri;
```

**Eğer hata almazsan:** ✅ Tablo başarıyla oluşturuldu!

---

## 🔧 SORUN GİDERME

### **Hata: relation "siramatik.siralar" does not exist**
- **Çözüm:** Önce diğer tabloları oluştur (siralar, kuyruklar, vb.)

### **Hata: permission denied for schema siramatik**
- **Çözüm:** Supabase Settings → Database → Extensions → `siramatik` şeması var mı kontrol et

### **Hata: violates foreign key constraint**
- **Çözüm:** `servis_id` NULL olabilir, ona izin ver:
```sql
ALTER TABLE siramatik.memnuniyet_anketleri 
ALTER COLUMN servis_id DROP NOT NULL;
```

---

## 📊 ŞİMDİ NE OLACAK?

Tablo oluştuktan sonra:

1. **Bilet sayfasından anket gönder**
   - Sırayı tamamla
   - Emoji seç
   - Gönder

2. **Kontrol et:**
```sql
SELECT 
    m.id,
    s.numara AS sira_no,
    k.ad AS kuyruk,
    m.puan,
    m.yorum,
    m.anket_tarihi
FROM siramatik.memnuniyet_anketleri m
LEFT JOIN siramatik.siralar s ON m.sira_id = s.id
LEFT JOIN siramatik.kuyruklar k ON m.kuyruk_id = k.id
ORDER BY m.anket_tarihi DESC
LIMIT 10;
```

---

## 🎯 ÖZET

1. ✅ Supabase SQL Editor'e git
2. ✅ Yukarıdaki SQL'i kopyala
3. ✅ RUN butonuna bas
4. ✅ Tabloyu kontrol et
5. ✅ Anket göndermeyi test et

**Süre:** ~2 dakika

---

**Not:** Eğer `database/08_memnuniyet.sql` dosyasını kullanıyorsan, o dosyadaki TÜMÜNÜ kopyala/yapıştır. İçinde fonksiyonlar da var (raporlama için).
