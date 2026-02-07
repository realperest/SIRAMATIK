# SIRAMATIK PROJE KURALLARI

Bu dosyada, projede çalışan tüm AI asistanlarının (Agent) uyması gereken katı kurallar yer almaktadır. Lütfen kod yazmadan önce bu kuralları dikkatlice okuyun.

## 🚨 KRİTİK VERİTABANI KURALLARI

1.  **TEK SCHEMA KURALI:**
    *   Veritabanında **SADECE** `siramatik` şeması (schema) kullanılacaktır.
    *   `public` şemasına **ASLA** tablo oluşturulmamalı, veri yazılmamalı ve veri okunmamalıdır.
    *   Eğer bir bağlantı stringi veya konfigürasyon `public` şemasına işaret ediyorsa, derhal `siramatik` olarak düzeltilmelidir.

2.  **SUPABASE CLIENT BAĞLANTISI:**
    *   Frontend tarafında (`bilet.html`, `kiosk.html`, `panel.html` vb.) Supabase JS client başlatılırken **MUTLAKA** şema belirtilmelidir:
        ```javascript
        const _supabase = supabase.createClient(supabaseUrl, supabaseKey, { db: { schema: 'siramatik' } });
        ```

3.  **BACKEND SQL SORGULARI:**
    *   Python backend (`database.py` vb.) içinde yazılan tüm ham SQL sorgularında tablo isimleri **şema ön eki ile** yazılmalıdır.
    *   Örnek DOĞRU: `SELECT * FROM siramatik.siralar`
    *   Örnek YANLIŞ: `SELECT * FROM siralar`
    *   SQLAlchemy veya ORM kullanırken de `schema="siramatik"` parametresi veya `search_path` ayarının doğru yapılandırıldığından emin olunmalıdır.

## 🏗 GENEL MİMARİ & GELİŞTİRME

1.  **Frontend:**
    *   HTML/JS/CSS (Vanilla) yapısı korunmalıdır.
    *   `bilet.html`: Müşteri takip ekranıdır (Mobile-first).
    *   `kiosk.html`: Bilet alma ekranıdır.
    *   `tv.html` / `panel.html`: Bekleme salonu ekranıdır.
    *   `personel.html` / `admin.html`: Gişe/Yönetim ekranıdır.

2.  **Backend:**
    *   FastAPI (Python) tabanlıdır.
    *   Veritabanı işlemleri `backend/database.py` üzerinden yürütülür.

3.  **Hata Yönetimi:**
    *   Veritabanı bağlantı hataları veya şema uyumsuzlukları durumunda kullanıcıya net hata mesajları gösterilmemeli, ancak console/log kayıtlarına detaylı yazılmalıdır.
