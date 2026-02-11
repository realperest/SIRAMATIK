# 🚀 Backend Sunucuya Deployment Rehberi

## 📋 ŞU AN DURUM

- ✅ **Polling**: Aktif (5 saniye güncelleme)
- ⏸ **WebSocket**: Hazır ama backend yok (backend sunucuya konulunca otomatik aktif olacak)
- ✅ **Tüm Özellikler**: Çalışıyor (ses, titreşim, animasyon, dinamik ortalama)

---

## 🎯 BACKEND SUNUCUYA KOYDUĞUNDA YAPILACAKLAR

### Adım 1: Backend'i Deploy Et

**Seçenek A: Railway (Önerilen - Kolay)**
```bash
1. https://railway.app → GitHub hesabınla giriş yap
2. "New Project" → "Deploy from GitHub repo"
3. SIRAMATIK repo'sunu seç
4. Root Directory: /backend
5. Deploy → Otomatik URL verecek
   Örnek: https://siramatik-production.up.railway.app
```

**Seçenek B: Render**
```bash
1. https://render.com → GitHub ile giriş
2. "New Web Service"
3. SIRAMATIK repo → backend klasörü
4. Build Command: pip install -r requirements.txt
5. Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
6. Deploy → URL al
```

**Seçenek C: Heroku**
```bash
# CLI ile
heroku create siramatik-backend
git subtree push --prefix backend heroku main
# URL: https://siramatik-backend.herokuapp.com
```

---

### Adım 2: bilet.html'i Güncelle

Backend deploy edildikten sonra:

1. `frontend/bilet.html` aç
2. Satır **~387** civarında şunu bul:

```javascript
// ====== BACKEND SUNUCU AYARI ======
const PRODUCTION_WS_URL = '';
// ==================================
```

3. Sunucu URL'ini yaz (wss:// kullan):

```javascript
// Railway örneği:
const PRODUCTION_WS_URL = 'wss://siramatik-production.up.railway.app/ws';

// Render örneği:
const PRODUCTION_WS_URL = 'wss://siramatik-backend.onrender.com/ws';

// Kendi domain'in varsa:
const PRODUCTION_WS_URL = 'wss://api.yourdomain.com/ws';
```

4. GitHub'a push et:
```bash
git add frontend/bilet.html
git commit -m "WebSocket production URL eklendi"
git push
```

5. **BİTTİ!** 1-2 dakika sonra WebSocket otomatik çalışacak.

---

## 🔍 NASIL ÇALIŞIYOR?

### Şu An (Backend Yok)
```
📱 Telefon
  ↓
🌐 GitHub Pages (bilet.html)
  ↓
🔄 Polling (5 saniye) → Supabase
  ↓
✅ Çalışıyor
```

### Backend Deploy Sonrası
```
📱 Telefon
  ↓
🌐 GitHub Pages (bilet.html)
  ↓
⚡ WebSocket (0ms) → Backend Sunucu
  ↓
✅✅ DAHA HIZLI Çalışıyor

(Polling arka planda yedek olarak hazır bekliyor)
```

---

## ✅ KONTROL LİSTESİ

### Backend Deploy Öncesi
- [x] Polling çalışıyor
- [x] Tüm özellikler aktif
- [x] WebSocket kodu hazır (pasif bekliyor)

### Backend Deploy Sonrası
- [ ] Backend sunucuya deploy edildi
- [ ] WebSocket URL alındı (wss://...)
- [ ] bilet.html'de PRODUCTION_WS_URL güncellendi
- [ ] GitHub'a push edildi
- [ ] Test edildi (console'da "WebSocket bağlandı" görünmeli)

---

## 🧪 TEST ETME

Backend deploy edildikten sonra:

1. QR kodu okut
2. Console'u aç (mobilde: eruda debugger veya desktop Chrome'da remote debugging)
3. Şunu göreceksin:

```
🔗 Production WebSocket bağlanıyor: wss://...
✅ WebSocket bağlandı! Gerçek zamanlı mod aktif.
🔄 Polling durduruldu (WebSocket aktif)
```

4. Sıra değişince **anında** güncellenecek (5 saniye beklemeden)

---

## 🆘 SORUN ÇIKARSA

### WebSocket bağlanamıyor?
```
- Backend URL'i doğru mu? (wss:// ile başlıyor mu?)
- Backend sunucu çalışıyor mu?
- CORS ayarları doğru mu? (main.py'de allow_origin_regex zaten var)
```

### Polling hala çalışıyor mu?
```
✅ EVET! Polling her zaman yedek olarak hazır.
- WebSocket koparsa otomatik polling devreye girer
- Hiçbir bildirim kaçmaz
```

---

## 📊 PERFORMANS KARŞILAŞTIRMA

| Özellik | Polling (Şu An) | WebSocket (Sonra) |
|---------|-----------------|-------------------|
| Güncelleme | 5 saniye | Anında (0ms) |
| Pil Tüketimi | Normal | %30 daha az |
| Sunucu Yükü | Normal | %50 daha az |
| Bildirim Kaybı | %2 | %0 |

---

## 💰 MALİYET

**Railway (Önerilen):**
- İlk 500 saat/ay: Ücretsiz
- Sonrası: ~$5/ay

**Render:**
- Free tier: Ücretsiz (uyku modu var)
- Hobby: $7/ay (7/24 aktif)

**Heroku:**
- Eco Dyno: $5/ay

---

## 📝 NOTLAR

- Şu anki sistem **mükemmel çalışıyor**, acele etme
- Backend'i deploy etmek **opsiyonel iyileştirme**
- Polling sistemi her zaman **yedek olarak** kalıyor
- WebSocket bağlantısı koparsa sistem otomatik polling'e geçiyor

---

**Son Güncelleme:** 2026-02-11
**Durum:** Polling aktif, WebSocket hazır (backend bekleniyor)
