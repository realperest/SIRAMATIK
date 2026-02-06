# Sıramatik - Veritabanı Şeması

PostgreSQL/Supabase için sıra yönetim sistemi veritabanı.

## 🎯 Özellikler

- ✅ **Multi-tenant**: Birden fazla firma/kurum desteği
- ✅ **Esnek Kuyruk Sistemi**: Bir servis içinde birden fazla kuyruk
- ✅ **VIP/Öncelik Sistemi**: Öncelikli sıra numaraları (0-9 arası öncelik)
- ✅ **Sektör-agnostik**: Hastane, banka, belediye vb. için uygun
- ✅ **IoT Desteği**: ESP32 cihaz entegrasyonu
- ✅ **GDPR/KVKK Uyumlu**: Otomatik veri temizleme

## 📊 Veritabanı Yapısı

### Hiyerarşi

```
Firma (Organization)
  └── Servis (Service/Department)
       └── Kuyruk (Queue)
            └── Sıra (Ticket/Number)
```

### Örnek Senaryo: Laboratuvar

```
Demo Medical Center (Firma)
  └── Laboratory (Servis)
       ├── Blood Test Queue (Kuyruk A)
       │    ├── A001 (Normal)
       │    ├── A002 (Normal)
       │    └── VIP001 (Öncelikli)
       ├── Urine Test Queue (Kuyruk B)
       │    ├── B001
       │    └── B002
       └── X-Ray Queue (Kuyruk C)
            └── C001
```

## 📋 Tablolar

### 1. firmalar
Firma/kurum bilgileri (multi-tenant)

### 2. servisler
Hizmet noktaları (departman, şube, birim)
- Örnek: Laboratory, Registration, Pharmacy

### 3. kuyruklar ⭐ YENİ
Bir servis içinde birden fazla kuyruk
- Örnek: Kan Testi kuyruğu, İdrar Testi kuyruğu
- `oncelik`: 0-9 arası (VIP kuyruklar için)

### 4. kullanicilar
Sistem kullanıcıları
- Roller: `admin`, `staff`, `kiosk`, `screen`, `manager`

### 5. siralar
Sıra numaraları
- `oncelik`: 0 (normal) veya 1-9 (VIP/öncelikli)
- Durum: `waiting`, `calling`, `serving`, `completed`, `cancelled`, `no_show`

### 6. cihazlar
IoT cihazları
- Tipler: `button`, `kiosk`, `screen1`, `screen2`, `tablet`
- Bir cihaz belirli bir kuyruğa atanabilir

### 7. cihaz_olaylari
Cihaz aktivite logları

### 8. sistem_ayarlari
Global ayarlar (key-value)

## 🚀 Kurulum

### 1. Supabase Projesi Oluştur

1. [supabase.com](https://supabase.com) hesabı oluştur
2. Yeni proje oluştur
3. SQL Editor'ü aç

### 2. SQL Dosyalarını Çalıştır

**SIRASINA GÖRE** aşağıdaki dosyaları çalıştır:

```sql
-- 1. Schema oluştur
\i 01_schema.sql

-- 2. Tabloları oluştur
\i 02_tables.sql

-- 3. İndeksleri ekle
\i 03_indexes.sql

-- 4. Fonksiyonları ekle
\i 04_functions.sql

-- 5. Demo verileri ekle (opsiyonel)
\i 05_seed_data.sql
```

**Supabase SQL Editor'de:**
Her dosyanın içeriğini kopyala → SQL Editor'e yapıştır → Run

## 🔧 Fonksiyonlar

### yeni_sira_numarasi(kuyruk_id, oncelik)
Otomatik sıra numarası üretir
- Normal: `A001`, `B042`
- VIP: `VIP001`, `VIP002`

```sql
SELECT siramatik.yeni_sira_numarasi(
    'kuyruk-uuid-here',
    0  -- 0: Normal, 1-9: VIP
);
```

### bekleyen_sira_sayisi(kuyruk_id, oncelik)
Bekleyen sıra sayısını döndürür

```sql
-- Tüm bekleyenler
SELECT siramatik.bekleyen_sira_sayisi('kuyruk-uuid');

-- Sadece VIP bekleyenler
SELECT siramatik.bekleyen_sira_sayisi('kuyruk-uuid', 5);
```

### siradaki_kisi(kuyruk_id)
Sıradaki kişiyi getirir (öncelik > zaman)

```sql
SELECT * FROM siramatik.siradaki_kisi('kuyruk-uuid');
```

### ortalama_bekleme_suresi(kuyruk_id, gun_sayisi)
Ortalama bekleme süresini dakika olarak döndürür

```sql
SELECT siramatik.ortalama_bekleme_suresi('kuyruk-uuid', 7);
```

### gunluk_istatistikler(firma_id, tarih)
Günlük istatistikler (VIP sayısı dahil)

```sql
SELECT * FROM siramatik.gunluk_istatistikler(
    'firma-uuid',
    CURRENT_DATE
);
```

### eski_siralari_temizle(gun_sayisi)
Eski sıraları temizle (GDPR/KVKK)

```sql
SELECT siramatik.eski_siralari_temizle(180);
```

## 📝 Örnek Sorgular

### Sıra Al (Normal)

```sql
INSERT INTO siramatik.siralar (kuyruk_id, servis_id, firma_id, numara, oncelik)
VALUES (
    'kuyruk-uuid',
    'servis-uuid',
    'firma-uuid',
    siramatik.yeni_sira_numarasi('kuyruk-uuid', 0),
    0
);
```

### VIP Sıra Al

```sql
INSERT INTO siramatik.siralar (kuyruk_id, servis_id, firma_id, numara, oncelik)
VALUES (
    'kuyruk-uuid',
    'servis-uuid',
    'firma-uuid',
    siramatik.yeni_sira_numarasi('kuyruk-uuid', 9),
    9  -- Yüksek öncelik
);
```

### Bekleyen Sıraları Listele (Öncelik Sırasına Göre)

```sql
SELECT * FROM siramatik.siralar
WHERE kuyruk_id = 'kuyruk-uuid'
AND durum = 'waiting'
ORDER BY oncelik DESC, olusturulma ASC;
```

### Bir Servisteki Tüm Kuyrukları Göster

```sql
SELECT 
    s.ad as servis_ad,
    k.ad as kuyruk_ad,
    k.kod,
    k.oncelik,
    COUNT(q.id) FILTER (WHERE q.durum = 'waiting') as bekleyen
FROM siramatik.servisler s
LEFT JOIN siramatik.kuyruklar k ON s.id = k.servis_id
LEFT JOIN siramatik.siralar q ON k.id = q.kuyruk_id
WHERE s.id = 'servis-uuid'
GROUP BY s.ad, k.ad, k.kod, k.oncelik;
```

## 🔐 Güvenlik

### Row Level Security (RLS) - Önerilen

```sql
-- Firmaların sadece kendi verilerini görmesi
ALTER TABLE siramatik.siralar ENABLE ROW LEVEL SECURITY;

CREATE POLICY firma_isolation ON siramatik.siralar
    FOR ALL
    USING (firma_id = current_setting('app.current_firma_id')::uuid);
```

## 🧹 Bakım

### Günlük Temizlik (Cron Job)

```sql
-- Her gün 03:00'da eski verileri temizle
SELECT cron.schedule(
    'cleanup-old-queues',
    '0 3 * * *',
    $$SELECT siramatik.eski_siralari_temizle(180)$$
);
```

## 📊 Demo Veriler

`05_seed_data.sql` çalıştırıldığında:

- ✅ 1 Demo firma
- ✅ 3 Servis (Laboratory, Registration, Pharmacy)
- ✅ 7 Kuyruk (Kan testi, İdrar testi, vb.)
- ✅ 3 Kullanıcı (admin@demo.com / admin123)
- ✅ Örnek sıralar (VIP dahil)

## 🎯 Kullanım Senaryoları

### Hastane
- **Servis**: Laboratuvar
- **Kuyruklar**: Kan Testi (A), İdrar Testi (B), X-Ray (C)
- **VIP**: Acil hastalar için öncelikli sıra

### Banka
- **Servis**: Gişe Hizmetleri
- **Kuyruklar**: Para Yatırma (A), Para Çekme (B), Kredi İşlemleri (C)
- **VIP**: Kurumsal müşteriler

### Belediye
- **Servis**: Nüfus Müdürlüğü
- **Kuyruklar**: Kimlik (A), Evlilik (B), Vukuatlı Nüfus (C)
- **VIP**: Engelli vatandaşlar

## 📞 Destek

Sorularınız için issue açın veya dokümantasyona bakın.

---

**Sıramatik** - Esnek ve ölçeklenebilir sıra yönetimi 🚀
