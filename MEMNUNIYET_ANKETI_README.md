# 🎯 MÜŞTERİ MEMNUNİYET ANKETİ SİSTEMİ

## 📋 GENEL BAKIŞ

Müşteriler hizmetlerini tamamladıktan sonra, aldıkları hizmeti 1-5 yıldız arasında puanlayabilir ve opsiyonel olarak yorum bırakabilirler.

---

## ✨ ÖZELLİKLER

### **Kullanıcı Deneyimi**
- ✅ 5 seviye emoji (😞 😕 😐 😊 😍)
- ✅ Opsiyonel yorum alanı
- ✅ Tek tıkla gönderim
- ✅ Teşekkür mesajı
- ✅ Mobil optimize tasarım

### **Teknik Özellikler**
- ✅ Otomatik gösterim (durum: `completed`)
- ✅ Tek anket garantisi (localStorage kontrol)
- ✅ Hizmet süresi tracking
- ✅ IP ve cihaz bilgisi kaydı
- ✅ Kullanıcı bazlı performans takibi

---

## 🗄️ DATABASE YAPISI

### **Tablo: `siramatik.memnuniyet_anketleri`**

| Alan | Tip | Açıklama |
|------|-----|----------|
| `id` | SERIAL | Primary key |
| `sira_id` | INTEGER | Sıra referansı |
| `kuyruk_id` | INTEGER | Kuyruk referansı |
| `servis_id` | INTEGER | Servis referansı |
| `firma_id` | INTEGER | Firma referansı |
| `cagiran_kullanici_id` | INTEGER | Hizmet veren personel |
| `puan` | INTEGER | 1-5 arası puan |
| `yorum` | TEXT | Müşteri yorumu (opsiyonel) |
| `anket_tarihi` | TIMESTAMPTZ | Anket gönderilme zamanı |
| `ip_adresi` | VARCHAR(45) | IP adresi |
| `cihaz_bilgisi` | TEXT | Cihaz bilgisi |
| `hizmet_suresi_dk` | INTEGER | Hizmet alma süresi (dakika) |

---

## 📊 RAPORLAMA FONKSİYONLARI

### **1. Kullanıcı Performansı**
```sql
SELECT * FROM siramatik.kullanici_ortalama_puan(kullanici_id, gun_sayisi);
```

**Dönen Veriler:**
- Kullanıcı ID ve adı
- Toplam anket sayısı
- Ortalama puan (0.00-5.00)
- Puan dağılımı (1-5 için ayrı ayrı)

**Örnek:**
```sql
SELECT * FROM siramatik.kullanici_ortalama_puan(5, 30);
-- Son 30 gündeki performans
```

---

### **2. Servis Memnuniyet Raporu**
```sql
SELECT * FROM siramatik.servis_memnuniyet_raporu(firma_id, gun_sayisi);
```

**Dönen Veriler:**
- Servis ID ve adı
- Toplam anket sayısı
- Ortalama puan
- Memnuniyet yüzdesi (4-5 puan alanlar)

**Örnek:**
```sql
SELECT * FROM siramatik.servis_memnuniyet_raporu(1, 7);
-- Son 7 günün servis bazlı analizi
```

---

### **3. Günlük Trend Analizi**
```sql
SELECT * FROM siramatik.gunluk_memnuniyet_trendi(firma_id, gun_sayisi);
```

**Dönen Veriler:**
- Tarih
- Günlük anket sayısı
- Günlük ortalama puan
- Günlük memnuniyet yüzdesi

**Örnek:**
```sql
SELECT * FROM siramatik.gunluk_memnuniyet_trendi(1, 30);
-- Son 30 günün trend grafiği için
```

---

## 🎨 KULLANICI AKIŞI

### **Senaryo: Müşteri Hizmetini Tamamladı**

```
1. Personel sırayı "Tamamla" yapar
   ↓
2. Bilet ekranında durum "completed" olur
   ↓
3. Anket formu otomatik gösterilir
   ↓
4. Müşteri emoji seçer (😞 😕 😐 😊 😍)
   ↓
5. İsteğe bağlı yorum yazar
   ↓
6. "Gönder" butonuna basar
   ↓
7. Supabase'e kaydedilir
   ↓
8. "🎉 Teşekkür Ederiz!" mesajı
   ↓
9. 3 saniye sonra form gizlenir
```

---

## 💻 API ENDPOINTLERİ

### **POST /api/memnuniyet/anket**

**Request Body:**
```json
{
  "sira_id": 123,
  "kuyruk_id": 5,
  "servis_id": 2,
  "firma_id": 1,
  "cagiran_kullanici_id": 10,
  "puan": 5,
  "yorum": "Çok memnun kaldım!",
  "hizmet_suresi_dk": 15
}
```

**Response:**
```json
{
  "success": true,
  "anket_id": 42,
  "message": "Anket kaydedildi, teşekkür ederiz!"
}
```

**Durum Kodları:**
- `200`: Başarılı
- `400`: Geçersiz puan (1-5 dışı)
- `500`: Sunucu hatası

---

## 🔧 KURULUM

### **1. Database Migration**

```bash
# PostgreSQL'e bağlan
psql -U postgres -d siramatik

# Migration dosyasını çalıştır
\i database/08_memnuniyet.sql
```

**Veya Supabase SQL Editor'de:**
```sql
-- database/08_memnuniyet.sql içeriğini kopyala/yapıştır
```

### **2. Backend Test**

Backend çalışırken:
```bash
curl -X POST http://localhost:8000/api/memnuniyet/anket \
  -H "Content-Type: application/json" \
  -d '{
    "sira_id": 1,
    "kuyruk_id": 1,
    "servis_id": 1,
    "firma_id": 1,
    "puan": 5,
    "yorum": "Test yorumu"
  }'
```

### **3. Frontend Test**

1. Bir sıra oluştur (kiosk'tan)
2. Personel panelden sırayı çağır
3. Personel panelden sırayı tamamla
4. Bilet sayfasında anket formu görünecek

---

## 📈 RAPORLAMA ÖRNEKLERİ

### **Örnek 1: En İyi Performans Gösteren Personel**

```sql
SELECT 
    k.ad AS personel,
    COUNT(m.id) AS toplam_anket,
    ROUND(AVG(m.puan), 2) AS ortalama_puan,
    ROUND((COUNT(m.id) FILTER (WHERE m.puan >= 4) * 100.0 / COUNT(m.id)), 2) AS memnuniyet_yuzdesi
FROM siramatik.kullanicilar k
LEFT JOIN siramatik.memnuniyet_anketleri m ON k.id = m.cagiran_kullanici_id
WHERE m.anket_tarihi > NOW() - INTERVAL '30 days'
GROUP BY k.id, k.ad
HAVING COUNT(m.id) >= 5  -- En az 5 anket
ORDER BY ortalama_puan DESC, memnuniyet_yuzdesi DESC
LIMIT 10;
```

### **Örnek 2: Düşük Puan Alanlar (Aksiyon Gerekli)**

```sql
SELECT 
    m.id,
    s.numara AS sira_no,
    k.ad AS kuyruk,
    m.puan,
    m.yorum,
    m.anket_tarihi,
    u.ad AS personel
FROM siramatik.memnuniyet_anketleri m
JOIN siramatik.siralar s ON m.sira_id = s.id
JOIN siramatik.kuyruklar k ON m.kuyruk_id = k.id
LEFT JOIN siramatik.kullanicilar u ON m.cagiran_kullanici_id = u.id
WHERE m.puan <= 2  -- Kötü ve Çok Kötü
    AND m.anket_tarihi > NOW() - INTERVAL '7 days'
ORDER BY m.anket_tarihi DESC;
```

### **Örnek 3: Aylık Trend Grafiği**

```sql
WITH monthly_stats AS (
    SELECT 
        TO_CHAR(anket_tarihi AT TIME ZONE 'Europe/Istanbul', 'YYYY-MM') AS ay,
        COUNT(*) AS toplam,
        ROUND(AVG(puan), 2) AS ort_puan,
        COUNT(*) FILTER (WHERE puan = 5) AS mukemmel,
        COUNT(*) FILTER (WHERE puan = 4) AS iyi,
        COUNT(*) FILTER (WHERE puan = 3) AS normal,
        COUNT(*) FILTER (WHERE puan = 2) AS kotu,
        COUNT(*) FILTER (WHERE puan = 1) AS cok_kotu
    FROM siramatik.memnuniyet_anketleri
    WHERE firma_id = 1
        AND anket_tarihi > NOW() - INTERVAL '12 months'
    GROUP BY ay
    ORDER BY ay DESC
)
SELECT 
    ay,
    toplam,
    ort_puan,
    ROUND((mukemmel + iyi) * 100.0 / toplam, 2) AS memnuniyet_yuzdesi,
    mukemmel, iyi, normal, kotu, cok_kotu
FROM monthly_stats;
```

---

## 🎯 KPI'LAR (Anahtar Performans Göstergeleri)

### **Hedef Değerler:**

| KPI | Hedef | Uyarı | Kritik |
|-----|-------|-------|--------|
| Ortalama Puan | ≥ 4.5 | < 4.0 | < 3.5 |
| Memnuniyet % | ≥ 85% | < 70% | < 60% |
| Yanıt Oranı | ≥ 40% | < 30% | < 20% |
| 1-2 Puan Oranı | ≤ 5% | > 10% | > 15% |

### **Hesaplama:**

```sql
WITH kpi AS (
    SELECT 
        ROUND(AVG(puan), 2) AS ort_puan,
        ROUND((COUNT(*) FILTER (WHERE puan >= 4) * 100.0 / COUNT(*)), 2) AS memnuniyet_yuzdesi,
        ROUND((COUNT(*) FILTER (WHERE puan <= 2) * 100.0 / COUNT(*)), 2) AS dusuk_puan_yuzdesi,
        COUNT(*) AS toplam_anket,
        (SELECT COUNT(*) FROM siramatik.siralar WHERE durum = 'completed' AND olusturulma > NOW() - INTERVAL '30 days') AS toplam_islem
    FROM siramatik.memnuniyet_anketleri
    WHERE anket_tarihi > NOW() - INTERVAL '30 days'
)
SELECT 
    *,
    ROUND((toplam_anket * 100.0 / NULLIF(toplam_islem, 0)), 2) AS yanit_orani
FROM kpi;
```

---

## 🔐 GÜVENLİK

### **RLS Politikaları**
- ✅ Herkes okuyabilir (raporlama için)
- ✅ Herkes ekleyebilir (anon - bilet sayfası)
- ✅ Sadece authenticated güncelleyebilir
- ✅ Silme yasak (veri bütünlüğü)

### **Validasyon**
- ✅ Puan: 1-5 arası (CHECK constraint)
- ✅ Sıra: Foreign key ile kontrol
- ✅ IP ve cihaz bilgisi log

---

## 📱 MOBIL GÖRÜNüM

```
┌───────────────────────────┐
│  🎯 Aldığınız Hizmeti     │
│     Puanlayın             │
├───────────────────────────┤
│  😞  😕  😐  😊  😍     │
│  (Tıklanan vurgulanır)    │
├───────────────────────────┤
│  Diyeceğiniz bir şey      │
│  var mı?                  │
│  ┌─────────────────────┐  │
│  │ [Yorum alanı]       │  │
│  └─────────────────────┘  │
├───────────────────────────┤
│     [  GÖNDER  ]          │
└───────────────────────────┘
```

---

## 🚀 SONRAKI ADIMLAR

### **Admin Paneline Eklenecekler:**
1. Memnuniyet raporu sayfası
2. Grafik ve trendler
3. Düşük puan uyarıları
4. Personel karşılaştırması
5. Excel export

### **AG-Grid Analiz Entegrasyonu:**
- Memnuniyet pivot tabloları
- Personel performans matrisi
- Zaman serileri analizi

---

**Tarih:** 2026-02-11  
**Versiyon:** 1.0  
**Durum:** ✅ Aktif ve Çalışıyor
