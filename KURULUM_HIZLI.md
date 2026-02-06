# 🚀 SIRAMATIK - Hızlı Kurulum Kılavuzu (PUBLIC Schema)

## 📋 Kurulum Adımları

### 1️⃣ Supabase SQL Editor'ü Aç

```
https://supabase.com/dashboard/project/wyursjdrnnjabpfeucyi/sql
```

### 2️⃣ SQL Dosyalarını Sırayla Çalıştır

**ÖNEMLİ:** `*_public.sql` dosyalarını kullanın! (Supabase uyumlu)

#### ✅ ADIM 1: Schema Hazırla (Opsiyonel)

```sql
-- Sadece yorum satırı, çalıştırmaya gerek yok
-- Tablolar public schema'da oluşturulacak
```

---

#### ✅ ADIM 2: Tabloları Oluştur

1. "New query" butonuna tıkla
2. `D:\KODLAMALAR\GITHUB\SIRAMATIK\database\02_tables_public.sql` dosyasını aç
3. Tüm içeriği kopyala-yapıştır
4. **RUN** butonuna bas
5. ✅ "Success" mesajını gör

**Oluşturulan Tablolar:**
- `firmalar` - Firma/kurum bilgileri
- `servisler` - Hizmet noktaları
- `kuyruklar` - Kuyruk tipleri ⭐ YENİ
- `kullanicilar` - Sistem kullanıcıları
- `siralar` - Sıra numaraları (VIP desteği)
- `cihazlar` - IoT cihazları
- `cihaz_olaylari` - Cihaz logları
- `sistem_ayarlari` - Global ayarlar

---

#### ✅ ADIM 3: İndeksleri Ekle

1. Yeni query
2. `03_indexes_public.sql` kopyala-yapıştır
3. **RUN**
4. ✅ İndeksler eklendi

---

#### ✅ ADIM 4: Fonksiyonları Ekle

1. Yeni query
2. `04_functions_public.sql` kopyala-yapıştır
3. **RUN**
4. ✅ 6 fonksiyon eklendi

**Fonksiyonlar:**
- `yeni_sira_numarasi()` - VIP sıra üretme
- `bekleyen_sira_sayisi()` - Bekleyen sayısı
- `siradaki_kisi()` - Öncelikli sıralama
- `ortalama_bekleme_suresi()` - İstatistik
- `gunluk_istatistikler()` - Raporlar
- `eski_siralari_temizle()` - GDPR temizlik

---

#### ✅ ADIM 5: Demo Verileri Ekle

1. Yeni query
2. `05_seed_data_public.sql` kopyala-yapıştır
3. **RUN**
4. ✅ "Demo veriler başarıyla eklendi!" mesajını gör

**Demo İçerik:**
- 1 Firma: Demo Medical Center
- 3 Servis: Laboratory, Registration, Pharmacy
- 7 Kuyruk: Kan Testi, İdrar Testi, X-Ray, vb.
- VIP kuyruk örnekleri
- 3 Kullanıcı (admin@demo.com / admin123)

---

### 3️⃣ Kurulumu Doğrula

SQL Editor'de:

```sql
-- Tabloları kontrol et
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public'
AND table_name IN ('firmalar', 'servisler', 'kuyruklar', 'siralar', 'kullanicilar', 'cihazlar', 'cihaz_olaylari', 'sistem_ayarlari')
ORDER BY table_name;

-- Demo verileri kontrol et
SELECT * FROM firmalar;
SELECT * FROM servisler;
SELECT * FROM kuyruklar;
SELECT * FROM siralar ORDER BY oncelik DESC, olusturulma;
```

**Beklenen:** 8 tablo, demo veriler

---

### 4️⃣ Backend Bağlantısını Test Et

```powershell
cd D:\KODLAMALAR\GITHUB\SIRAMATIK\database
python test_backend_connection.py
```

**Beklenen Çıktı:**
```
✅ Supabase client oluşturuldu
✅ 1 firma bulundu: Demo Medical Center
✅ 3 servis bulundu
✅ 7 kuyruk bulundu
🎉 BAŞARILI! Backend Supabase'e bağlanabilir.
```

---

### 5️⃣ Backend'i Başlat

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

**Test:**
```
http://localhost:8000/api/servisler/11111111-1111-1111-1111-111111111111
```

---

### 6️⃣ Frontend'i Başlat

```powershell
cd D:\KODLAMALAR\GITHUB\SIRAMATIK\frontend
python -m http.server 3000
```

**Sayfalar:**
- Kiosk: http://localhost:3000/kiosk.html
- Staff: http://localhost:3000/staff.html
- Screen: http://localhost:3000/screen.html

---

## 🔐 Demo Giriş

**Email:** admin@demo.com  
**Şifre:** admin123

---

## 🎯 Özellikler

### ✅ Kuyruk Sistemi
```
Laboratory Servisi
  ├── Blood Test (A) → A001, A002, A003
  ├── Urine Test (B) → B001, B002
  └── X-Ray (C) → C001
```

### ✅ VIP/Öncelik
- Normal: A001, A002
- VIP: VIP001, VIP002 (öncelik: 9)
- Sıralama: Öncelik > Zaman

### ✅ Sektör-Agnostik
- Hastane, Banka, Belediye, Restoran...

---

## 📝 Sonra: Custom Schema'ya Geçiş

Sistem çalıştıktan sonra `siramatik` schema'sına geçmek için:

1. Supabase Dashboard > Settings > API > Exposed schemas
2. `siramatik` ekle
3. Orijinal `*.sql` dosyalarını çalıştır
4. Backend'de `.schema('siramatik')` ekle

Detaylar: `database/SCHEMA_COZUMU.md`

---

## ❓ Sorun Giderme

### Backend bağlanamıyor
```powershell
cd database
python test_backend_connection.py
```

### Tablolar görünmüyor
```sql
SELECT * FROM information_schema.tables WHERE table_schema = 'public';
```

### Fonksiyonlar çalışmıyor
```sql
SELECT routine_name FROM information_schema.routines WHERE routine_schema = 'public';
```

---

**Başarılar! 🎉**

Sorularınız için: `database/README.md`
