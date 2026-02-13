# Sıramatik - Zaman Karşılaştırmaları Mantığı

## Genel Prensip

**Kayıtlar yerel saat ile kaydedilir, sorgulama da yerel saate göre yapılır.**

## 1. Kayıt Oluşturma (INSERT/UPDATE)

### Kullanım:
```python
local_now = db.get_local_now()  # → "NOW() + INTERVAL '3 hours'"
```

### Örnek:
```sql
INSERT INTO siramatik.siralar (olusturulma) 
VALUES (NOW() + INTERVAL '3 hours')
-- Sonuç: 14:00 (yerel saat) olarak kaydedilir
```

## 2. Sorgulama (SELECT)

### A) Direkt Okuma (Timestamp)
```python
# Kayıtlar zaten yerel saat ile kaydedildiği için direkt okunur
SELECT olusturulma FROM siramatik.siralar
-- Sonuç: 14:00 (direkt okunur, ek dönüşüm yok)
```

### B) Tarih Karşılaştırması (Bugünkü Kayıtlar)
```python
# Bugünkü kayıtları filtrele
today_filter = db._today_filter_sql("s.olusturulma")
# → "AND s.olusturulma::date = (NOW() + INTERVAL '3 hours')::date"
```

**Mantık:**
- Kayıt: `14:00` (yerel saat) olarak kaydedilmiş
- Bugün: `(NOW() + 3 hours)::date` = `2024-01-15` (yerel tarih)
- Karşılaştırma: `14:00::date` = `2024-01-15` → ✅ Eşleşir

### C) Zaman Karşılaştırması (Son X Dakika/Saat)

#### Son 20 Dakika İçindeki Kayıtlar:
```python
local_20min_ago = db._local_now_minus_interval("20 minutes")
# → "(NOW() + INTERVAL '3 hours' - INTERVAL '20 minutes')"

# Kullanım:
WHERE s.cagirilma > {local_20min_ago}
```

**Mantık:**
- Şu an: `14:00` (yerel saat)
- 20 dakika önce: `13:40` (yerel saat)
- Kayıt: `13:50` (yerel saat) olarak kaydedilmiş
- Karşılaştırma: `13:50 > 13:40` → ✅ Eşleşir

#### Son 5 Dakika İçindeki Kayıtlar:
```python
local_5min_ago = db._local_now_minus_interval("5 minutes")
# → "(NOW() + INTERVAL '3 hours' - INTERVAL '5 minutes')"

# Kullanım:
WHERE cagirilma < {local_5min_ago}
```

## 3. Online/Offline Durumu

### Cihaz Online/Offline Kontrolü:
```python
local_now = db.get_local_now()  # → "NOW() + INTERVAL '3 hours'"

# Kullanım:
CASE 
    WHEN c.son_gorulen > ({local_now} - INTERVAL '30 seconds') THEN 'online'
    ELSE 'offline'
END
```

**Mantık:**
- Şu an: `14:00:00` (yerel saat)
- 30 saniye önce: `13:59:30` (yerel saat)
- Son görülme: `14:00:10` (yerel saat) olarak kaydedilmiş
- Karşılaştırma: `14:00:10 > 13:59:30` → ✅ Online

## 4. Önemli Kurallar

### ✅ DOĞRU:
1. **Kayıt oluştururken:** `get_local_now()` kullan (yerel saat ile kaydet)
2. **Sorgulama yaparken:** Direkt oku (ek dönüşüm yok)
3. **Tarih filtreleri:** `_local_date_sql()` ve `_today_local_sql()` kullan
4. **Zaman karşılaştırmaları:** `_local_now_minus_interval()` veya `_local_now_plus_interval()` kullan

### ❌ YANLIŞ:
1. **Kayıt oluştururken:** `NOW()` kullanma (UTC olarak kaydeder)
2. **Sorgulama yaparken:** `AT TIME ZONE 'UTC'` kullanma (çift dönüşüm yapar)
3. **Zaman karşılaştırmaları:** `NOW() - INTERVAL` kullanma (UTC'ye göre karşılaştırır)

## 5. Örnek Senaryolar

### Senaryo 1: Bugünkü Bekleyen Sıralar
```python
# Kayıt: 14:00 (yerel saat) olarak kaydedilmiş
# Bugün: 2024-01-15 (yerel tarih)

today_filter = db._today_filter_sql("s.olusturulma")
# → "AND s.olusturulma::date = (NOW() + INTERVAL '3 hours')::date"

# Sonuç: ✅ Bugünkü kayıtlar bulunur
```

### Senaryo 2: Son 20 Dakika İçinde Çağrılan Sıralar
```python
# Şu an: 14:00 (yerel saat)
# 20 dakika önce: 13:40 (yerel saat)
# Kayıt: 13:50 (yerel saat) olarak kaydedilmiş

local_20min_ago = db._local_now_minus_interval("20 minutes")
# → "(NOW() + INTERVAL '3 hours' - INTERVAL '20 minutes')"

WHERE s.cagirilma > {local_20min_ago}
# Sonuç: ✅ 13:50 > 13:40 → Bulunur
```

### Senaryo 3: Cihaz Online/Offline Durumu
```python
# Şu an: 14:00:00 (yerel saat)
# 30 saniye önce: 13:59:30 (yerel saat)
# Son görülme: 14:00:10 (yerel saat) olarak kaydedilmiş

local_now = db.get_local_now()
# → "NOW() + INTERVAL '3 hours'"

CASE 
    WHEN c.son_gorulen > ({local_now} - INTERVAL '30 seconds') THEN 'online'
    ELSE 'offline'
END
# Sonuç: ✅ 14:00:10 > 13:59:30 → Online
```

## 6. Timezone Offset Değişikliği

Eğer timezone offset değiştirilirse (örn: 3 → 6):
- **Yeni kayıtlar:** Yeni offset ile kaydedilir
- **Eski kayıtlar:** Eski offset ile kaydedilmiş (değişmez)
- **Sorgulama:** Yeni offset ile yapılır (tutarsızlık olabilir)

**Öneri:** Timezone offset değiştirilmeden önce eski kayıtları da güncellemek gerekebilir.

## 7. Test

Test scripti: `backend/test_timezone.py`

```bash
cd backend
python test_timezone.py
```

Bu script:
- Timezone offset'i gösterir
- `get_local_now()` SQL ifadesini gösterir
- Veritabanındaki zamanları gösterir
- Son kayıtları gösterir
