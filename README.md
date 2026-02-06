# 🎉 SIRAMATIK - PROJE HAZIR!

## ✅ Tamamlanan İşler

### 1. Veritabanı Şeması
- ✅ Kuyruk sistemi (bir servis → birden fazla kuyruk)
- ✅ VIP/Öncelik sistemi (0-9 arası)
- ✅ Sektör-agnostik terminoloji
- ✅ 8 Tablo + 6 Fonksiyon
- ✅ PUBLIC schema versiyonu (Supabase uyumlu)
- ✅ SIRAMATIK schema versiyonu (gelecek için)

### 2. Backend API
- ✅ FastAPI RESTful API
- ✅ JWT authentication
- ✅ Kuyruk ve VIP endpoints
- ✅ Supabase entegrasyonu
- ✅ .env yapılandırması

### 3. Dokümantasyon
- ✅ Hızlı kurulum kılavuzu
- ✅ Detaylı README
- ✅ Schema çözüm dokümanı
- ✅ Test scriptleri

---

## 📁 Dosya Yapısı

```
SIRAMATIK/
├── KURULUM_HIZLI.md ⭐ BURADAN BAŞLAYIN!
├── README.md
├── database/
│   ├── 01_schema_public.sql ✅ PUBLIC
│   ├── 02_tables_public.sql ✅ PUBLIC (8 tablo)
│   ├── 03_indexes_public.sql ✅ PUBLIC
│   ├── 04_functions_public.sql ✅ PUBLIC (6 fonksiyon)
│   ├── 05_seed_data_public.sql ✅ PUBLIC (demo)
│   ├── 01_schema.sql (gelecek: siramatik schema)
│   ├── 02_tables.sql (gelecek: siramatik schema)
│   ├── 03_indexes.sql (gelecek: siramatik schema)
│   ├── 04_functions.sql (gelecek: siramatik schema)
│   ├── 05_seed_data.sql (gelecek: siramatik schema)
│   ├── SCHEMA_COZUMU.md
│   ├── test_backend_connection.py
│   └── README.md
├── backend/
│   ├── main.py ✅
│   ├── database.py ✅
│   ├── models.py ✅
│   ├── auth.py ✅
│   ├── config.py ✅
│   ├── requirements.txt ✅
│   └── .env ✅ (Supabase bilgileri)
└── frontend/
    ├── kiosk.html
    ├── staff.html
    └── screen.html
```

---

## 🚀 Hızlı Başlangıç (3 Adım)

### 1️⃣ Supabase'de Tabloları Oluştur (5 dk)

```
https://supabase.com/dashboard/project/wyursjdrnnjabpfeucyi/sql
```

**Sırayla çalıştır:**
1. `02_tables_public.sql` → 8 tablo
2. `03_indexes_public.sql` → İndeksler
3. `04_functions_public.sql` → 6 fonksiyon
4. `05_seed_data_public.sql` → Demo veriler

**Detaylı talimatlar:** `KURULUM_HIZLI.md`

---

### 2️⃣ Backend'i Test Et (2 dk)

```powershell
cd database
python test_backend_connection.py
```

**Beklenen:**
```
✅ 1 firma bulundu: Demo Medical Center
✅ 3 servis bulundu
✅ 7 kuyruk bulundu
🎉 BAŞARILI!
```

---

### 3️⃣ Backend'i Başlat (2 dk)

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**Test:**
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

---

## 🎯 Özellikler

### ✅ Esnek Kuyruk Sistemi

```
Laboratory Servisi
  ├── Blood Test (A) → A001, A002, A003
  ├── Urine Test (B) → B001, B002
  └── X-Ray (C) → C001
```

### ✅ VIP/Öncelik Sistemi

- **Normal:** A001, A002, A003
- **VIP:** VIP001, VIP002 (öncelik: 9)
- **Sıralama:** Öncelik > Zaman

### ✅ Sektör-Agnostik

**Hastane:**
- Servis: Laboratuvar
- Kuyruklar: Kan Testi, İdrar Testi, X-Ray

**Banka:**
- Servis: Gişe Hizmetleri
- Kuyruklar: Para Yatırma, Para Çekme, Kredi

**Belediye:**
- Servis: Nüfus Müdürlüğü
- Kuyruklar: Kimlik, Evlilik, Vukuatlı

---

## 🔐 Demo Giriş

**Email:** admin@demo.com  
**Şifre:** admin123

**Diğer Kullanıcılar:**
- staff1@demo.com / admin123
- staff2@demo.com / admin123

---

## 📊 API Endpoints

### Sıra Al (Kiosk)
```http
POST /api/sira/al
{
  "kuyruk_id": "uuid",
  "servis_id": "uuid",
  "firma_id": "uuid",
  "oncelik": 0  // 0: Normal, 9: VIP
}
```

### Bekleyen Sıralar (Staff)
```http
GET /api/sira/bekleyenler/{kuyruk_id}
```

### Sıra Çağır (Staff)
```http
POST /api/sira/cagir/{sira_id}
{
  "kullanici_id": "uuid",
  "konum": "Oda 3"
}
```

### Kuyrukları Listele (Kiosk)
```http
GET /api/kuyruklar/{servis_id}
```

**Detaylı API Docs:** http://localhost:8000/docs

---

## 🔄 Gelecek: Custom Schema'ya Geçiş

Sistem çalıştıktan sonra `siramatik` schema'sına geçmek için:

1. **Supabase Dashboard**
   - Settings > API > Exposed schemas
   - `siramatik` ekle

2. **SQL Dosyaları**
   - `01_schema.sql` → `05_seed_data.sql` çalıştır

3. **Backend Güncelle**
   ```python
   # database.py
   self.client.schema('siramatik').table('firmalar')...
   ```

**Detaylar:** `database/SCHEMA_COZUMU.md`

---

## 📞 Destek & Kaynaklar

- **Hızlı Kurulum:** `KURULUM_HIZLI.md`
- **Veritabanı Detayları:** `database/README.md`
- **Schema Çözümü:** `database/SCHEMA_COZUMU.md`
- **API Docs:** http://localhost:8000/docs

---

## ✅ Checklist

- [ ] SQL dosyalarını Supabase'de çalıştır
- [ ] Backend bağlantısını test et
- [ ] Backend'i başlat
- [ ] API Docs'u kontrol et
- [ ] Frontend'i başlat
- [ ] Demo giriş yap
- [ ] Sıra al ve çağır

---

**Başarılar! 🎉**

Sorularınız için issue açın veya dokümantasyona bakın.
