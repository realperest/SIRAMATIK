-- Timezone Ayarını Kontrol Et
-- Bu sorguyu Supabase SQL Editor'den çalıştırın

SELECT 
    current_setting('timezone') as current_timezone,
    NOW() as current_time,
    CURRENT_TIMESTAMP as current_timestamp,
    LOCALTIMESTAMP as local_timestamp;

-- Beklenen Sonuç:
-- current_timezone: Europe/Istanbul
-- current_time: Şu anki yerel saat (UTC+3)
-- current_timestamp: Şu anki yerel saat (UTC+3)
-- local_timestamp: Şu anki yerel saat (UTC+3)
