# 🔧 Supabase Schema Sorunu ve Çözümleri

## ⚠️ Sorun

Supabase Python client REST API kullanır ve **varsayılan olarak sadece `public` schema'yı** destekler.

Bizim SQL dosyalarımız `siramatik` schema'sını kullanıyor:
```sql
CREATE SCHEMA siramatik;
CREATE TABLE siramatik.firmalar (...);
```

Backend'den bu tablolara erişemeyiz çünkü Supabase client sadece `public` schema'ya bakar.

---

## ✅ Çözüm 1: PUBLIC Schema Kullan (Önerilen - Kolay)

### Adımlar:

1. **SQL dosyalarındaki `siramatik.` önekini kaldır**

Tüm SQL dosyalarında:
```sql
-- ÖNCE:
CREATE TABLE siramatik.firmalar (...);

-- SONRA:
CREATE TABLE firmalar (...);
```

2. **Supabase SQL Editor'de çalıştır**

Dosyaları sırayla çalıştır:
- `01_schema_public.sql` (yeni dosya)
- `02_tables.sql` (düzenlenmiş)
- `03_indexes.sql` (düzenlenmiş)
- `04_functions.sql` (düzenlenmiş)
- `05_seed_data.sql` (düzenlenmiş)

### Avantajlar:
- ✅ Hemen çalışır
- ✅ Ekstra ayar gerektirmez
- ✅ Supabase Dashboard'da tablolar görünür

### Dezavantajlar:
- ⚠️ `public` schema kirlenir (çok fazla tablo varsa)

---

## ✅ Çözüm 2: Custom Schema + PostgREST Config (Gelişmiş)

### Adımlar:

1. **Supabase Dashboard'da schema'yı expose et**

```
Dashboard > Settings > API > Exposed schemas
```

`siramatik` schema'sını ekle.

2. **SQL dosyalarını olduğu gibi çalıştır**

`siramatik` schema'sı ile tabloları oluştur.

3. **Backend'de schema belirt**

```python
# database.py
result = self.client.schema('siramatik').table('firmalar').select('*').execute()
```

### Avantajlar:
- ✅ Temiz schema organizasyonu
- ✅ Multi-tenant için ideal

### Dezavantajlar:
- ⚠️ Supabase Dashboard'da manuel ayar gerekir
- ⚠️ Her tablo çağrısında `.schema('siramatik')` eklenmeli

---

## 🎯 Önerim: Çözüm 1 (PUBLIC Schema)

Proje basit olduğu için `public` schema kullanmak en pratik çözüm.

### Hızlı Uygulama:

1. `database/` klasöründe yeni dosyalar oluşturdum:
   - `01_schema_public.sql` ✅
   - Diğer dosyaları da güncelleyeceğim

2. Bu dosyaları Supabase'de çalıştır

3. Backend otomatik çalışacak

---

## 📝 Alternatif: Her İki Versiyonu da Hazırla

- `*_public.sql` → Public schema versiyonu (kolay)
- `*.sql` → Siramatik schema versiyonu (gelişmiş)

Hangisini kullanmak istersiniz?

---

**Devam edelim mi?** 
1. Public schema versiyonunu mu hazırlayayım? (Hızlı)
2. Custom schema ayarlarını mı göstereyim? (Gelişmiş)
