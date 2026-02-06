# 🚀 SIRAMATIK - Manuel Supabase Kurulum Kılavuzu

## ⚠️ Önemli Not
PostgreSQL pooler bağlantısı "Tenant or user not found" hatası veriyor. Bu nedenle **SQL Editor** ile manuel kurulum yapacağız.

## 📋 Kurulum Adımları

### 1️⃣ Supabase SQL Editor'ü Aç

Tarayıcınızda şu adresi açın:
```
https://supabase.com/dashboard/project/wyursjdrnnjabpfeucyi/sql
```

### 2️⃣ SQL Dosyalarını Sırayla Çalıştır

**ÖNEMLİ:** Dosyaları tam bu sırayla çalıştırın!

#### ✅ ADIM 1: Schema Oluştur

1. "New query" butonuna tıkla
2. `D:\KODLAMALAR\GITHUB\SIRAMATIK\database\01_schema.sql` dosyasını aç
3. Tüm içeriği kopyala
4. SQL Editor'e yapıştır
5. "RUN" butonuna bas
6. ✅ "Success" mesajını gör

```sql
-- Dosya içeriği:
CREATE SCHEMA IF NOT EXISTS siramatik;
ALTER DATABASE postgres SET search_path TO siramatik, public;
COMMENT ON SCHEMA siramatik IS 'Sıramatik QMS - Kuyruk Yönetim Sistemi';
```

---

#### ✅ ADIM 2: Tabloları Oluştur

1. Yeni query aç
2. `02_tables.sql` dosyasını aç
3. Tüm içeriği kopyala-yapıştır
4. RUN
5. ✅ 8 tablo oluşturuldu mesajını gör

**Oluşturulan Tablolar:**
- `siramatik.firmalar` - Firma/kurum bilgileri
- `siramatik.servisler` - Hizmet noktaları
- `siramatik.kuyruklar` - Kuyruk tipleri ⭐ YENİ
- `siramatik.kullanicilar` - Sistem kullanıcıları
- `siramatik.siralar` - Sıra numaraları (VIP desteği ile)
- `siramatik.cihazlar` - IoT cihazları
- `siramatik.cihaz_olaylari` - Cihaz logları
- `siramatik.sistem_ayarlari` - Global ayarlar

---

#### ✅ ADIM 3: İndeksleri Ekle

1. Yeni query
2. `03_indexes.sql` kopyala-yapıştır
3. RUN
4. ✅ İndeksler eklendi

---

#### ✅ ADIM 4: Fonksiyonları Ekle

1. Yeni query
2. `04_functions.sql` kopyala-yapıştır
3. RUN
4. ✅ 6 fonksiyon eklendi

**Fonksiyonlar:**
- `yeni_sira_numarasi()` - Otomatik sıra üretme (VIP desteği)
- `bekleyen_sira_sayisi()` - Bekleyen sayısı
- `siradaki_kisi()` - Sıradaki kişi (öncelik sırasına göre)
- `ortalama_bekleme_suresi()` - Ortalama bekleme
- `gunluk_istatistikler()` - Günlük raporlar
- `eski_siralari_temizle()` - GDPR/KVKK temizlik

---

#### ✅ ADIM 5: Demo Verileri Ekle

1. Yeni query
2. `05_seed_data.sql` kopyala-yapıştır
3. RUN
4. ✅ "Demo veriler başarıyla eklendi!" mesajını gör

**Demo İçerik:**
- 1 Firma: Demo Medical Center
- 3 Servis: Laboratory, Registration, Pharmacy
- 7 Kuyruk: Kan Testi, İdrar Testi, X-Ray, vb.
- VIP kuyruk örnekleri
- 3 Kullanıcı (admin@demo.com / admin123)

---

### 3️⃣ Kurulumu Doğrula

SQL Editor'de şu sorguyu çalıştır:

```sql
-- Tabloları kontrol et
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'siramatik'
ORDER BY table_name;

-- Demo verileri kontrol et
SELECT * FROM siramatik.firmalar;
SELECT * FROM siramatik.servisler;
SELECT * FROM siramatik.kuyruklar;
SELECT * FROM siramatik.siralar ORDER BY oncelik DESC, olusturulma;
```

**Beklenen Sonuç:**
- 8 tablo görünmeli
- 1 firma, 3 servis, 7 kuyruk
- Örnek sıralar (VIP dahil)

---

## 🚀 Backend Başlatma

Kurulum tamamlandıktan sonra:

```powershell
cd D:\KODLAMALAR\GITHUB\SIRAMATIK\backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**API Adresleri:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

---

## 🌐 Frontend Başlatma

```powershell
cd D:\KODLAMALAR\GITHUB\SIRAMATIK\frontend
python -m http.server 3000
```

**Sayfalar:**
- Kiosk: http://localhost:3000/kiosk.html
- Staff: http://localhost:3000/staff.html
- Screen: http://localhost:3000/screen.html

---

## 🔐 Demo Giriş Bilgileri

**Email:** admin@demo.com  
**Şifre:** admin123

**Diğer Kullanıcılar:**
- staff1@demo.com / admin123
- staff2@demo.com / admin123

---

## 🎯 Özellikler

### ✅ Kuyruk Sistemi
Bir servis içinde birden fazla kuyruk:
```
Laboratory Servisi
  ├── Blood Test (A)
  ├── Urine Test (B)
  └── X-Ray (C)
```

### ✅ VIP/Öncelik Sistemi
- `oncelik`: 0-9 arası
- 0: Normal sıra
- 1-9: Öncelikli sıra (VIP, acil, engelli vb.)
- VIP sıralar otomatik `VIP001`, `VIP002` formatında

### ✅ Sektör-Agnostik
- Hastane: Laboratuvar → Kan Testi, İdrar Testi
- Banka: Gişe → Para Yatırma, Para Çekme
- Belediye: Nüfus → Kimlik, Evlilik

---

## ❓ Sorun Giderme

### "Schema already exists" hatası
Normal, devam edin.

### "Permission denied" hatası
Supabase'de admin yetkileriniz olduğundan emin olun.

### Fonksiyonlar çalışmıyor
```sql
SHOW search_path;
SET search_path TO siramatik, public;
```

---

## 📞 Destek

Sorun yaşarsanız:
1. SQL Editor'de hata mesajını kontrol edin
2. `database/README.md` dosyasına bakın
3. Her adımı tek tek çalıştırın

---

**Başarılar! 🎉**
