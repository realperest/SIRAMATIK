# Özel Domain ile Bilet Linki (Alt Alan Adı + DNS)

Barkod/QR'da `realperest.github.io` yerine kendi domain'iniz (örn. **siramatik.inovathinks.com**) görünsün istiyorsanız bu rehberi uygulayın.

---

## 1. Alt alan adı (subdomain) nedir?

Zaten **inovathinks.com** gibi bir domain'iniz var. **Alt alan** = domain'in önüne bir isim eklemek:

- **siramatik.inovathinks.com** → "siramatik" alt alanı
- **bilet.inovathinks.com** → "bilet" alt alanı

Yeni bir domain satın almanız gerekmez; mevcut domain üzerinde DNS kaydı ekleyeceksiniz.

---

## 2. DNS ayarları (GoDaddy örneği)

### 2.1 GoDaddy’da DNS sayfasına girin

1. **godaddy.com** → Giriş yapın.
2. **My Products** (Ürünlerim) → **Domains** bölümünde domain'inize (örn. **inovathinks.com**) tıklayın.
3. **DNS** veya **DNS Management** / **DNS’i Yönet** butonuna tıklayın.
4. **Records** (Kayıtlar) listesini açın.

### 2.2 CNAME kaydı ekleyin

1. **Add** / **Ekle** (veya **Add Record** / **Kayıt Ekle**) butonuna tıklayın.
2. **Type (Tür):** **CNAME** seçin.
3. **Name (Ad):** Alt alan adını yazın. Sadece ön ek:
   - `siramatik` yazarsanız → **siramatik.inovathinks.com** olur.
   - `bilet` yazarsanız → **bilet.inovathinks.com** olur.
4. **Value (Değer) / Points to (Yönlendir):**
   - **Tam olarak:** `realperest.github.io`
   - Sonunda nokta (.) veya slash (/) olmasın.
5. **TTL:** Varsayılan (600 veya 1 hour) bırakabilirsiniz.
6. **Save** / **Kaydet** deyin.

Özet tablo:

| Type | Name   | Value                 |
|------|--------|------------------------|
| CNAME| siramatik | realperest.github.io |

### 2.3 Yayılmasını bekleyin

DNS değişikliği 5 dakika – 48 saat arasında yayılır; çoğu zaman 15–30 dakikada etkili olur.

---

## 3. GitHub Pages’te özel domain tanımlama

1. **github.com** → **realperest/SIRAMATIK** reposuna gidin.
2. **Settings** → solda **Pages**.
3. **Custom domain** kutusuna tam adresi yazın:
   - `siramatik.inovathinks.com`
   - Sonunda `/` olmasın.
4. **Save** deyin.
5. İsterseniz **Enforce HTTPS** kutusunu işaretleyin (bir süre sonra HTTPS açılır).

---

## 4. Projede bilet linkini güncelleme

1. **frontend/kiosk.html** dosyasını açın.
2. Şu satırı bulun:
   ```javascript
   const BILET_QR_BASE_URL = 'https://realperest.github.io/SIRAMATIK';
   ```
3. Şöyle değiştirin:
   ```javascript
   const BILET_QR_BASE_URL = 'https://siramatik.inovathinks.com';
   ```
4. Kaydedip repoya push edin. Artık barkod/QR’da bu adres görünür.

---

## 5. Kontrol

- Tarayıcıda **https://siramatik.inovathinks.com** açın; bilet sayfası (veya ana sayfa) GitHub Pages’teki gibi açılıyorsa DNS ve GitHub ayarı doğrudur.
- Kiosk’ta yeni numara alıp çıkan barkodu taratın; link **siramatik.inovathinks.com** ile başlamalı.

---

## Sık karşılaşılan sorunlar

- **“Sayfa açılmıyor”:** DNS henüz yayılmamış olabilir; birkaç saat bekleyin veya farklı ağdan/telefondan deneyin.
- **“Certificate / HTTPS hatası”:** GitHub bir süre sonra SSL verir; **Enforce HTTPS** açıksa 24 saate kadar bekleyin.
- **GoDaddy’da CNAME yok:** Bazı arayüzlerde **CNAME Record** veya **CNAME Alias** diye geçer; aynı alan adına (örn. siramatik) ve değer olarak `realperest.github.io` yazın.

Bu adımlarla hosting almadan, sadece domain’inizin DNS’i ve GitHub Pages ayarıyla barkod linkini kendi alt alan adınızda gösterebilirsiniz.
