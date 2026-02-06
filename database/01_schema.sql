-- ============================================
-- SIRAMATIK VERITABANI ŞEMASI
-- PostgreSQL 15+ / Supabase
-- ============================================

-- 1. SCHEMA OLUŞTUR
CREATE SCHEMA IF NOT EXISTS siramatik;

-- 2. Schema'yı varsayılan arama yoluna ekle
ALTER DATABASE postgres SET search_path TO siramatik, public;

-- Not: Supabase'de bu komutu çalıştıramazsanız, 
-- her sorgunuzda "siramatik.tablo_adi" şeklinde kullanın

COMMENT ON SCHEMA siramatik IS 'Sıramatik QMS - Hastane Sıra Yönetim Sistemi';
