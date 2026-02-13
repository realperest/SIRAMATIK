# Supabase Timezone Kurulumu

## Önemli: Bu adımı mutlaka yapın!

Supabase veritabanında timezone'u ayarlamak için aşağıdaki adımları izleyin:

### 1. Supabase Dashboard'a Giriş

1. [Supabase Dashboard](https://supabase.com/dashboard) adresine gidin
2. Projenizi seçin (1BIR)
3. Sol menüden **SQL Editor**'e tıklayın

### 2. SQL Scripti Çalıştırma

1. `backend/set_supabase_timezone.sql` dosyasını açın
2. İçeriğini kopyalayın
3. Supabase SQL Editor'e yapıştırın
4. **Run** butonuna tıklayın

### 3. Kontrol

Script çalıştıktan sonra şu sorguyu çalıştırarak kontrol edin:

```sql
SELECT current_setting('timezone') as current_timezone, NOW() as current_time;
```

**Beklenen Sonuç:**
- `current_timezone`: `Europe/Istanbul`
- `current_time`: Şu anki yerel saat (UTC+3)

### 4. Sonuç

✅ Artık tüm `NOW()` çağrıları (hem backend hem frontend) yerel saati döndürecek
✅ `bilet.html`'deki manuel +3 saat kodu kaldırıldı
✅ Tüm timestamp'ler tutarlı şekilde yerel saat ile işlenecek

### Notlar

- Bu ayar **veritabanı seviyesinde** yapılır
- Tüm bağlantılar (backend, frontend, Supabase client) aynı timezone'u kullanır
- Ayar kalıcıdır, veritabanı yeniden başlatılsa bile korunur

### Sorun Giderme

Eğer `ALTER DATABASE` komutu çalışmazsa (yetki hatası):
- Supabase Free tier'da bu komut çalışmayabilir
- Alternatif: Connection string'de timezone ayarlanabilir (backend'de zaten yapıldı)
- Frontend için: `bilet.html`'deki manuel +3 saat kodunu geri ekleyin
