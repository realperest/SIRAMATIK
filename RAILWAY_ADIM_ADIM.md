# Railway Build Hatası – Adım Adım Çözüm

"Error creating build plan with Railpack" hatasını gidermek için aşağıdaki adımları **sırayla** uygulayın.

---

## Adım 1: Repo’daki dosyaları kontrol et

Bilgisayarınızda proje klasöründe:

1. **backend/requirements.txt** şöyle olmalı (UTF-8, satır başına tek paket):
   - İçinde `fastapi`, `uvicorn`, `sqlalchemy`, `psycopg2-binary` vb. tek satırda yazılı olmalı; karakterler arasında boşluk olmamalı.
2. **backend/Procfile** şu satırı içermeli:
   - `web: uvicorn main:app --host 0.0.0.0 --port $PORT`

Bu iki dosya doğruysa bir sonraki adıma geçin.

---

## Adım 2: Değişiklikleri GitHub’a gönder

Eğer `requirements.txt` veya `Procfile` üzerinde değişiklik yaptıysanız ve henüz push etmediyseniz:

1. Terminalde proje kökünde:
   ```bash
   git add backend/requirements.txt backend/Procfile
   git commit -m "fix: Railway icin requirements.txt ve Procfile"
   git push origin main
   ```
2. Push’un GitHub’a gittiğini kontrol edin.

---

## Adım 3: Railway’da Root Directory’yi ayarla

Bu adım **en önemli**. Root Directory boşsa build tüm repoyu tarar ve “Error creating build plan with Railpack” hatası oluşur.

1. Tarayıcıda **https://railway.app** adresine gidin ve giriş yapın.
2. **SIRAMATIK** projesine tıklayın.
3. Sol tarafta veya ortada **SIRAMATIK** servis kartına tıklayın (backend servisi).
4. Üstteki sekmelerden **Settings**’e tıklayın.
5. Sayfayı aşağı kaydırın; **Source** veya **Repository** bölümünü bulun.
6. **Root Directory** (veya “Build directory”) alanını bulun.
   - Şu an büyük ihtimalle **boş**.
7. Bu alana **sadece** şunu yazın: `backend`  
   (küçük harf, tırnak yok, başında/sonunda boşluk yok.)
8. Değişikliği **kaydedin** (Save / Update vb. buton varsa tıklayın).

---

## Adım 4: Yeni bir deploy başlat (Redeploy)

1. Aynı serviste üstte **Deployments** sekmesine tıklayın.
2. Sağ üstte **Redeploy** veya **Deploy** butonu varsa tıklayın.  
   **Veya:** Son deployment satırındaki üç nokta (⋮) menüsünden **Redeploy** seçin.
3. Build log’u izleyin:
   - **Build > Build image** yeşil tik alırsa build başarılı demektir.
   - Hâlâ “Error creating build plan with Railpack” görürseniz **Adım 3**’ü tekrar kontrol edin; Root Directory gerçekten `backend` olmalı.

---

## Adım 5: Build başarılıysa – Domain ve URL

1. **Settings** sekmesine dönün.
2. **Networking** / **Public Networking** bölümüne girin.
3. **Generate Domain** (veya **Add Domain**) tıklayın.
4. Verilen URL’i kopyalayın (örnek: `https://siramatik-production-xxxx.up.railway.app`).  
   URL’in sonunda **slash (/) olmasın**.

---

## Adım 6: Frontend’de backend adresini güncelle

1. Projede **frontend/bilet.html** dosyasını açın.
2. **BILET_BACKEND_URL** (veya benzeri backend URL’i) satırını bulun.
3. Değeri Railway’dan aldığınız URL ile değiştirin, örneğin:
   ```javascript
   const BILET_BACKEND_URL = 'https://siramatik-production-xxxx.up.railway.app';
   ```
4. Dosyayı kaydedin, gerekirse commit + push yapın.

---

## Özet kontrol listesi

- [ ] **backend/requirements.txt** UTF-8 ve düzgün satır formatında.
- [ ] **backend/Procfile** var ve `web: uvicorn main:app --host 0.0.0.0 --port $PORT` yazıyor.
- [ ] Değişiklikler **GitHub’a push** edildi.
- [ ] Railway’da **Root Directory = backend** (Settings → Source).
- [ ] **Redeploy** yapıldı ve build **başarılı**.
- [ ] **Generate Domain** ile URL alındı.
- [ ] **bilet.html** içinde **BILET_BACKEND_URL** bu URL ile güncellendi.

Bu adımları tamamladıktan sonra build hâlâ fail ediyorsa, Railway’daki **Build Logs** çıktısının son 20–30 satırını paylaşırsanız bir sonraki adımı netleştirebiliriz.
