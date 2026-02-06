# Sıramatik - SQL Kurulum Talimatları

## 🎯 Supabase 1BIR Projesi - Manuel Kurulum

### Bağlantı Bilgileri
- **Project URL:** https://wyursjdrnnjabpfeucyi.supabase.co
- **Database Password:** qk4SEnyhu3NUk2

### 📝 Kurulum Adımları

1. **SQL Editor'ü Aç**
   ```
   https://supabase.com/dashboard/project/wyursjdrnnjabpfeucyi/sql
   ```

2. **Yeni Query Oluştur**
   - "New query" butonuna tıkla

3. **SQL Dosyalarını Sırayla Çalıştır**

#### ✅ ADIM 1: Schema Oluştur
Dosya: `01_schema.sql`

```sql
-- SIRAMATIK VERITABANI ŞEMASI
CREATE SCHEMA IF NOT EXISTS siramatik;
ALTER DATABASE postgres SET search_path TO siramatik, public;
COMMENT ON SCHEMA siramatik IS 'Sıramatik QMS - Kuyruk Yönetim Sistemi';
```

**Çalıştır** → "Success" mesajını bekle

---

#### ✅ ADIM 2: Tabloları Oluştur
Dosya: `02_tables.sql`

Bu dosyanın tamamını kopyala ve çalıştır:
- 8 tablo oluşturulacak (firmalar, servisler, kuyruklar, kullanicilar, siralar, cihazlar, cihaz_olaylari, sistem_ayarlari)

**Çalıştır** → "Success" mesajını bekle

---

#### ✅ ADIM 3: İndeksleri Ekle
Dosya: `03_indexes.sql`

Bu dosyanın tamamını kopyala ve çalıştır:
- Performans için indeksler oluşturulacak

**Çalıştır** → "Success" mesajını bekle

---

#### ✅ ADIM 4: Fonksiyonları Ekle
Dosya: `04_functions.sql`

Bu dosyanın tamamını kopyala ve çalıştır:
- 6 PostgreSQL fonksiyonu oluşturulacak

**Çalıştır** → "Success" mesajını bekle

---

#### ✅ ADIM 5: Demo Verileri Ekle
Dosya: `05_seed_data.sql`

Bu dosyanın tamamını kopyala ve çalıştır:
- Demo firma, servisler, kuyruklar ve örnek sıralar oluşturulacak

**Çalıştır** → "✅ Demo veriler başarıyla eklendi!" mesajını göreceksiniz

---

### 🔍 Doğrulama

Kurulum tamamlandıktan sonra test et:

```sql
-- Tabloları kontrol et
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'siramatik';

-- Demo verileri kontrol et
SELECT * FROM siramatik.firmalar;
SELECT * FROM siramatik.servisler;
SELECT * FROM siramatik.kuyruklar;
SELECT * FROM siramatik.siralar;
```

### 📊 Beklenen Sonuç

- ✅ 8 tablo oluşturulmuş
- ✅ 1 demo firma (Demo Medical Center)
- ✅ 3 servis (Laboratory, Registration, Pharmacy)
- ✅ 7 kuyruk (Kan Testi, İdrar Testi, X-Ray, vb.)
- ✅ Örnek sıralar (VIP dahil)

### 🚀 Backend Başlatma

Kurulum tamamlandıktan sonra:

```bash
cd D:\KODLAMALAR\GITHUB\SIRAMATIK\backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Backend: http://localhost:8000
API Docs: http://localhost:8000/docs

### 🌐 Frontend Başlatma

```bash
cd D:\KODLAMALAR\GITHUB\SIRAMATIK\frontend
python -m http.server 3000
```

- Kiosk: http://localhost:3000/kiosk.html
- Staff: http://localhost:3000/staff.html
- Screen: http://localhost:3000/screen.html

---

## 🔐 Demo Giriş Bilgileri

**Email:** admin@demo.com
**Şifre:** admin123

---

## ❓ Sorun Giderme

### "Schema already exists" hatası
Normal, devam edin.

### "Permission denied" hatası
Supabase'de admin yetkileriniz olduğundan emin olun.

### Fonksiyonlar çalışmıyor
`search_path` ayarını kontrol edin:
```sql
SHOW search_path;
SET search_path TO siramatik, public;
```
