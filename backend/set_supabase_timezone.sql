-- Supabase Veritabanı Timezone Ayarı
-- Bu script Supabase SQL Editor'den çalıştırılmalıdır
-- 
-- NOT: Bu komut veritabanı seviyesinde timezone'u ayarlar.
-- Artık tüm NOW() çağrıları (hem backend hem frontend) yerel saati döndürecek.
-- 
-- Çalıştırmadan önce:
-- 1. Supabase Dashboard > SQL Editor'e gidin
-- 2. Bu scripti yapıştırın
-- 3. "Run" butonuna tıklayın

-- Timezone'u Europe/Istanbul (UTC+3) olarak ayarla
ALTER DATABASE postgres SET timezone TO 'Europe/Istanbul';

-- Ayarı kontrol et
SELECT current_setting('timezone') as current_timezone, NOW() as current_time;

-- NOT: Bu ayar tüm bağlantılar için geçerlidir.
-- Backend ve Frontend (Supabase client) aynı timezone'u kullanacaktır.
