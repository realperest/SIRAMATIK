# Railway’de SIRAMATIK Backend Ayarları

Bu rehber, backend’i Railway’e sıfırdan bağlamak ve doğru ayarlarla çalıştırmak için adım adım yapmanız gerekenleri anlatır.

---

## 1. GitHub’da repo görünmüyorsa

- Railway’de **New Project** → **Deploy from GitHub repo** açıldığında arama kutusuna **SIRAMATIK** veya **realperest/SIRAMATIK** yazın.
- **“No repositories found”** çıkıyorsa:
  1. **Configure GitHub App** (veya dişli ikon) tıklayın.
  2. Açılan sayfada **Repository access** bölümünde:
     - **All repositories** seçin **veya**
     - **Only select repositories** → **SIRAMATIK** (realperest/SIRAMATIK) ekleyin.
  3. **Save** deyip Railway’e dönün, sayfayı yenileyin.
  4. Tekrar **SIRAMATIK** arayın; repo listede çıkmalı.

---

## 2. Projeyi oluşturma ve repo seçme

1. **railway.app** → Giriş yapın (GitHub ile).
2. **+ New** → **Deploy from GitHub repo** (veya **Create a New Project** altında GitHub seçeneği).
3. Arama kutusuna **SIRAMATIK** yazın.
4. **realperest/SIRAMATIK** reposunu seçin.
5. Railway projeyi oluşturup ilk deploy’u başlatır; bu aşamada **Root Directory** henüz ayarlı olmayabilir.

---

## 3. Root Directory mutlaka `backend` yapın (Build hatası bu yüzden olabilir)

Backend kodu repoda **backend** klasöründe; Railway’in build alırken sadece bu klasörü kullanması gerekir. Root Directory boş bırakılırsa tüm repo taranır, Railpack "Error creating build plan" verebilir.

1. Oluşan projede **SIRAMATIK servisine** tıklayın.
2. Üstte **Settings** sekmesine girin.
3. Solda **Source** bölümüne inin; **Root Directory** alanını bulun.
4. Değeri **`backend`** yapın (tırnak yok, küçük harf).
5. Kaydedin; Railway yeni bir deploy tetikleyecektir.

**Kontrol:** Build log'da `prepare_mac_requirements.py`, `append_ws.py`, `seed_data.py` gibi repo kökündeki dosya isimleri görünüyorsa Root Directory hâlâ boş demektir — mutlaka **backend** yazıp tekrar deploy edin.

---

## 4. Build ve başlatma komutları (gerekirse)

Railway çoğu zaman Python projelerini otomatik algılar. Algılamazsa veya hata alırsanız:

- **Build Command** (isteğe bağlı):  
  `pip install -r requirements.txt`  
  (Root Directory `backend` ise `requirements.txt` zaten `backend` içinden okunur.)

- **Start Command** (gerekirse manuel verin):  
  `uvicorn main:app --host 0.0.0.0 --port $PORT`  
  Railway `PORT` ortam değişkenini kendisi verir.

Bu alanlar **Settings** → **Build** / **Deploy** bölümünde bulunur.

---

## 5. Ortam değişkenleri (Variables)

- Veritabanı: Şu an `backend/database.py` içinde bağlantı tanımlı olabilir. Production’da güvenlik için **Railway → Variables** kısmında `DATABASE_URL` tanımlayıp, uygulamanın bu değişkeni okuması tercih edilir.  
  Şimdilik mevcut haliyle çalışıyorsa Variables’a dokunmayabilirsiniz.
- **SECRET_KEY** vb. kullanıyorsanız onları da Variables’a ekleyin.

---

## 6. Public URL (domain) alma

1. Serviste **Settings** → **Networking** / **Public Networking**.
2. **Generate Domain** (veya **Add Domain**) tıklayın.
3. Örnek: `https://siramatik-production.up.railway.app` gibi bir URL verilir.
4. Bu URL’i kopyalayın; bilet sayfasında kullanacaksınız.

---

## 7. bilet.html’de backend adresini yazma

1. Repoda **frontend/bilet.html** dosyasını açın.
2. **BILET_BACKEND_URL** satırını bulun (ör. `const BILET_BACKEND_URL = '...'`).
3. Railway’den aldığınız URL’i yazın (sonunda `/` olmasın):

```javascript
const BILET_BACKEND_URL = 'https://SIZIN-RAILWAY-URL.iniz.up.railway.app';
```

4. WebSocket için aynı host, `wss://` ile kullanılır (kodda başka bir yerde tanımlıysa orayı da aynı domain ile güncelleyin).
5. Değişikliği commit edip GitHub’a push edin.

---

## 8. Çalıştığını kontrol etme

- Tarayıcıda:  
  `https://SIZIN-RAILWAY-URL.iniz.up.railway.app/health`  
  Açın; `{"status":"healthy"}` benzeri bir yanıt gelmeli.
- Bilet sayfasını (GitHub Pages) açıp erteleme vb. işlemleri deneyin; “Sunucu erişilebilir” mesajı ve isteklerin çalışması gerekir.

---

## 9. Otomatik deploy (her push’ta)

- Proje **GitHub repo’ya bağlı** olduğu sürece, `main` branch’e (veya Railway’de seçtiğiniz branch’e) **push** yaptığınızda yeni deploy otomatik başlar.
- **Deployments** sekmesinden son deploy’ları ve durumlarını (Building → Deploying → Success) görebilirsiniz.

---

## Kısa kontrol listesi

| Adım | Yapılacak |
|------|------------|
| 1 | GitHub App’te SIRAMATIK reposuna erişim verin. |
| 2 | New Project → Deploy from GitHub → SIRAMATIK seçin. |
| 3 | Servis Settings → **Root Directory: `backend`** yapın. |
| 4 | Build/Start komutları gerekirse ekleyin (uvicorn + PORT). |
| 5 | Generate Domain ile URL alın. |
| 6 | frontend/bilet.html içinde **BILET_BACKEND_URL** = bu URL. |
| 7 | /health ile test edin; bilet sayfasından erteleme deneyin. |

Bu adımlarla Railway ayarlarını tamamlayabilirsiniz.
