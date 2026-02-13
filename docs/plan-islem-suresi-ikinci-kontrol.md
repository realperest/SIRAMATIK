# Bilet / Kapanış Kontrolleri

## Gece yarısı sıfırlama

**Evet.** Bilet numaraları (K001, X002, …) her gün **001’den yeniden başlar**. Bunun için ayrı bir “gece yarısı job” yok: `get_next_manuel_numara` sadece **bugün** (yerel tarih) oluşturulan biletlere bakıyor; ertesi gün aynı ön ek (K, X vb.) için yine 001’den sayıyor. Yani sıra numarası her gün (yerel gece yarısıyla) fiilen sıfırlanmış oluyor.

---

# İkinci Kontrol: Unutulan Bilet & İşlem Süresi Sapması

**Problem:** Personel "Bitir" / "Sıradakini çağır" demediğinde bilet `serving` kalıyor → işlem süresi gereksiz uzun görünüyor veya sabaha kalıyor.

---

## Öneri 1: Personel panelinde "Unutulan bilet" uyarısı (öncelikli)

**Ne:** Aktif bilet (serving) belirli bir süreyi (örn. **15 veya 20 dakika**) aşınca personel paneline uyarı.

**Nasıl:**
- Personel panelinde zaten **İşlem Süresi** sayacı var (active-ticket-timer).
- Bu süre örn. **≥ 15 dakika** olduğunda:
  - Bir **toast** veya küçük **banner**: *"Bu bilet 15 dakikadır işlemde. Müşteri ayrıldıysa lütfen **Bitir** ile kapatın."*
  - İsteğe bağlı: 15 dk’da bir tekrarlayan uyarı (spam olmaması için günde 1–2 kez veya sadece ilk geçişte).

**Avantaj:** Personel unutunca hatırlatılır; "Bitir" demeyi alışkanlık haline getirir.  
**Dezavantaj:** Unutma devam ederse yine uzun süre kalabilir → Öneri 2 ve 3 ile desteklenmeli.

---

## Öneri 2: İstatistikte işlem süresi tavanı (cap)

**Ne:** Ortalama işlem süresi hesaplanırken **aşırı uzun** tek biletler ortalamayı şişirmesin.

**Nasıl:**
- İstatistik sorgularında (örn. `get_gunluk_istatistik`, raporlar) işlem süresi hesabında:
  - **Tavan:** Tek bir biletin işlem süresi örn. **en fazla 60 dakika** sayılsın.
  - SQL örneği: `LEAST(EXTRACT(EPOCH FROM (tamamlanma - COALESCE(islem_baslangic, cagirilma)))/60, 60)` ile tek bilet süresi 60 dk ile sınırlanır; ortalama buna göre hesaplanır.
- Alternatif: İşlem süresi **> 60 dk** olan biletleri ortalamaya **hiç dahil etme** (outlier kabul et).

**Avantaj:** Unutulan bir bilet 5 saat de kalsa ortalamayı tek başına bozmaz.  
**Dezavantaj:** Gerçekten çok uzun süren nadir işlemler de "60 dk" gibi görünür; raporlarda not edilebilir.

---

## Öneri 3: Mesai bitiminde "hâlâ işlemde" biletleri toplu kapatma

**Ne:** ÇIKIŞ / mesai bitimi akışında, "bekleyen biletleri atalım mı?" sorusuna ek olarak: **Hâlâ serving/calling kalan biletler** varsa bunları da sor.

**Nasıl:**
- Mesai bitiminden sonra (hafta içi 17:30’dan sonra, cumartesi 14:00’dan sonra herhangi bir zamanda) ÇIKIŞ’e basıldığında:
  1. **Bekleyen (waiting)** biletler → zaten var: *"Bekleyen X bilet var, çöpe atalım mı?"*
  2. **İşlemde (serving) veya çağrılmış (calling)** kalan biletler → yeni: *"Y bilet hâlâ işlemde görünüyor. Hepsini tamamlandı olarak işaretleyelim mi?"*
- Evet derse: Bu biletleri `durum = 'completed'`, `tamamlanma = NOW()` ile kapat. İstatistikte Öneri 2 (tavan) varsa zaten sapma sınırlı kalır.

**Avantaj:** Sabaha "serving" kalan bilet kalmaz; ertesi gün karışıklık olmaz.  
**Dezavantaj:** Aslında devam eden bir işlem yoksa bile "tamamlandı" yapılmış olur; mesai bitiminde genelde makul.

---

## Öneri 4: Gece yarısı / zamanlanmış kontrol (isteğe bağlı)

**Ne:** Gece yarısı (veya sabah 00:30) bir job çalışsın; hâlâ **serving** veya **calling** kalan tüm biletleri:
- Ya **completed** yap (tamamlanma = çağrılma + 1 saat gibi sabit),
- Ya **discarded** benzeri bir duruma al (istatistiğe dahil etme).

**Avantaj:** Hiç kimse çıkış yapmasa bile sabaha "takılı" bilet kalmaz.  
**Dezavantaj:** Zamanlanmış job altyapısı gerekir (cron, Celery, vs.); şu an yoksa ek iş.

---

## Uygulama sırası önerisi

| Sıra | Öneri | Zorluk | Etki |
|------|--------|--------|------|
| 1 | **Öneri 1** – Personel panelinde 15 dk uyarı | Düşük | Unutmayı azaltır |
| 2 | **Öneri 2** – İstatistikte 60 dk tavan | Düşük | Ortalama sapmasını önler |
| 3 | **Öneri 3** – Mesai bitiminde "işlemde kalan"ları kapat | Orta | Sabaha serving kalmaz |

Önce **1 + 2** uygulanabilir; **3** mesai bitimi akışına eklenerek ikinci kontrol tamamlanır. **4** ileride otomasyon istenirse düşünülebilir.
