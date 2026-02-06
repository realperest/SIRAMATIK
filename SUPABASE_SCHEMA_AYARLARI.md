# 🔧 Supabase Siramatik Schema Yapılandırması

## ✅ Durum

- ✅ Public schema temizlendi
- ✅ Siramatik schema'da 8 tablo var
- ❌ Backend henüz siramatik schema'yı kullanamıyor

---

## 📝 Supabase Dashboard Ayarları

### Adım 1: API Settings'e Git

```
https://supabase.com/dashboard/project/wyursjdrnnjabpfeucyi/settings/api
```

### Adım 2: Exposed Schemas

1. **"Exposed schemas"** bölümünü bul
2. Şu anda muhtemelen: `public`
3. Değiştir: `public,siramatik` veya sadece `siramatik`

### Adım 3: DB Schema (Önemli!)

1. **"DB Schema"** ayarını bul
2. Değiştir: `siramatik`

Bu ayar, PostgREST'in varsayılan olarak hangi schema'yı kullanacağını belirler.

### Adım 4: Kaydet ve Yeniden Başlat

1. **Save** butonuna tıkla
2. Supabase servisleri otomatik yeniden başlayacak (~30 saniye)

---

## 🧪 Test

Ayarları yaptıktan sonra:

```powershell
cd D:\KODLAMALAR\GITHUB\SIRAMATIK\database
python test_backend_schema.py
```

**Beklenen:**
```
✅ Firmalar okunabilir: 1 kayıt
```

---

## 🔄 Alternatif: SQL ile Schema Ayarı

Eğer Dashboard'da ayar bulamazsanız, SQL ile de yapabilirsiniz:

```sql
-- PostgREST config
ALTER ROLE authenticator SET search_path TO siramatik, public;
ALTER ROLE anon SET search_path TO siramatik, public;
ALTER ROLE authenticated SET search_path TO siramatik, public;

-- Restart gerektirir
```

---

## 📱 Backend Durumu

Backend şu anda çalışmıyor çünkü tablolar public'te yok.

**Supabase ayarlarını yaptıktan sonra:**

1. Backend'i yeniden başlat:
   ```powershell
   cd D:\KODLAMALAR\GITHUB\SIRAMATIK\backend
   python main.py
   ```

2. Test et:
   ```
   http://localhost:8000/docs
   ```

---

## ⚠️ Önemli Not

Supabase'de schema değişikliği yaptıktan sonra:
- PostgREST otomatik yeniden başlar
- Cache temizlenir
- ~30 saniye bekleyin

---

**Dashboard ayarlarını yaptıktan sonra bana haber verin!** 🚀
