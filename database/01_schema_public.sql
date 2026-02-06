-- ============================================
-- SIRAMATIK VERITABANI ŞEMASI
-- PostgreSQL 15+ / Supabase
-- PUBLIC SCHEMA VERSİYONU (Supabase Python Client için)
-- ============================================

-- Not: Supabase Python client REST API kullanır ve
-- sadece 'public' schema'yı destekler.
-- Bu nedenle tabloları public schema'da oluşturuyoruz.

-- Eğer 'siramatik' schema'sını kullanmak isterseniz,
-- Supabase Dashboard > Settings > API > Exposed schemas
-- kısmından 'siramatik' schema'sını ekleyin.

COMMENT ON SCHEMA public IS 'Sıramatik QMS - Kuyruk Yönetim Sistemi';
