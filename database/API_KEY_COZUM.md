# 🔑 Supabase API Key Sorunu - Çözüm

## ⚠️ Sorun

401 Unauthorized hatası alıyoruz. Bu, API key'in yanlış veya eksik olduğu anlamına gelir.

## ✅ Çözüm

### 1️⃣ Doğru API Key'i Al

1. Tarayıcıda aç:
   ```
   https://supabase.com/dashboard/project/wyursjdrnnjabpfeucyi/settings/api
   ```

2. **"API Keys"** sekmesinde:
   - `anon` `public` key'i bul
   - **COPY** butonuna tıkla
   - Tam key'i kopyala (çok uzun olacak, ~200+ karakter)

### 2️⃣ Backend .env Dosyasını Güncelle

`D:\KODLAMALAR\GITHUB\SIRAMATIK\backend\.env` dosyasını aç:

```env
SUPABASE_URL=https://wyursjdrnnjabpfeucyi.supabase.co
SUPABASE_KEY=<BURAYA_KOPYALADIĞINIZ_ANON_KEY>
```

**Örnek:**
```env
SUPABASE_URL=https://wyursjdrnnjabpfeucyi.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind5dXJzamRybm5qYWJwZmV1Y3lpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzg4NDI3NzcsImV4cCI6MjA1NDQxODc3N30.UZUN_BIR_STRING_BURAYA_GELECEK
```

### 3️⃣ Test Et

```powershell
cd D:\KODLAMALAR\GITHUB\SIRAMATIK\database
python test_supabase_rest.py
```

**Beklenen:**
```
✅ Client oluşturuldu
✅ Bağlantı başarılı
```

---

## 📝 Alternatif: Manuel Key Girişi

Eğer key'i kopyalayamıyorsanız:

1. Screenshot'taki "API Keys" sekmesini açın
2. `anon` key'in **tamamını** görün
3. Manuel olarak kopyalayın

**Not:** Key çok uzun olabilir, dikkatli kopyalayın!

---

## 🎯 Key Doğru mu Kontrol

Key şu formatta olmalı:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind5dXJzamRybm5qYWJwZmV1Y3lpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzg4NDI3NzcsImV4cCI6MjA1NDQxODc3N30.XXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

- 3 bölüm (`.` ile ayrılmış)
- İlk bölüm: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9`
- İkinci bölüm: Uzun string (project bilgileri)
- Üçüncü bölüm: İmza (signature)

---

## ⚡ Hızlı Test

Key'i aldıktan sonra:

```python
from supabase import create_client

supabase = create_client(
    "https://wyursjdrnnjabpfeucyi.supabase.co",
    "BURAYA_ANON_KEY"
)

# Test
response = supabase.table('firmalar').select('*').limit(1).execute()
print("✅ Çalışıyor!" if response else "❌ Hata")
```

---

**API Key'i aldıktan sonra bana bildirin, devam edelim!** 🚀
