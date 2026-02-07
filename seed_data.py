import random
from datetime import datetime, timedelta
from backend.database import db

def seed_dummy_data():
    firma_id = 1
    # Mevcut servisleri ve kuyrukları al
    servisler = db.get_servisler(firma_id)
    if not servisler:
        print("Hizmet bulunamadı, önce servis ekleyin.")
        return
    
    servis_ids = [s['id'] for s in servisler]
    kuyruklar = db.get_kuyruklar_by_firma(firma_id)
    kuyruk_map = {k['servis_id']: k['id'] for k in kuyruklar}

    print(f"Veri üretiliyor: {len(servis_ids)} servis için son 6 ay...")

    # Son 180 gün (yaklaşık 6 ay)
    now = datetime.now()
    start_date = now - timedelta(days=180)

    total_inserted = 0
    
    # Her gün için döngü
    current_date = start_date
    while current_date <= now:
        # Hafta sonu mu? (Yoğunluk farkı için)
        is_weekend = current_date.weekday() >= 5
        
        # Aylık dalgalanma (Sinüs dalgası gibi basit bir çarpan)
        month_factor = 1.0 + 0.3 * random.uniform(-1, 1)
        
        # Günlük baz adet (Ortalama ayda 500 bilet / 30 gün ~= 17 bilet/gün)
        # Ama kullanıcı "her ay 500" dediği için toplam 3000 bilet civarı.
        # Günlük 15-25 arası bilet üretelim.
        daily_count = int(random.randint(10, 30) * month_factor)
        if is_weekend:
            daily_count = int(daily_count * 0.4) # Hafta sonu daha az
        
        for _ in range(daily_count):
            # 08:00 - 18:00 arası rastgele saat
            hour = random.randint(8, 17)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            
            ts = current_date.replace(hour=hour, minute=minute, second=second)
            
            # Rastgele servis ve kuyruk
            sid = random.choice(servis_ids)
            kid = kuyruk_map.get(sid)
            
            if not kid: continue

            # Durum dağılımı
            rand_status = random.random()
            if rand_status < 0.8:
                durum = 'completed'
                tamamlanma = ts + timedelta(minutes=random.randint(5, 20))
                cagirilma = ts + timedelta(minutes=random.randint(1, 5))
            elif rand_status < 0.9:
                durum = 'waiting'
                tamamlanma = None
                cagirilma = None
            else:
                durum = 'calling'
                tamamlanma = None
                cagirilma = ts + timedelta(minutes=random.randint(0, 2))

            # SQL ile direkt göm (oncelik rastgele %10 VIP)
            oncelik = 1 if random.random() < 0.1 else 0
            
            # Numara formatı (Servis kodu + sıra)
            numara = f"T{random.randint(100, 999)}"

            db.execute_query("""
                INSERT INTO siramatik.siralar 
                (kuyruk_id, servis_id, firma_id, numara, oncelik, durum, olusturulma, cagirilma, tamamlanma)
                VALUES (:kid, :sid, :fid, :num, :onc, :dur, :olust, :cagir, :tamam)
            """, {
                "kid": kid, "sid": sid, "fid": firma_id, "num": numara,
                "onc": oncelik, "dur": durum, "olust": ts, "cagir": cagirilma, "tamam": tamamlanma
            })
            total_inserted += 1

        current_date += timedelta(days=1)
        if total_inserted % 500 == 0:
            print(f"{total_inserted} kayıt eklendi...")

    print(f"BİTTİ! Toplam {total_inserted} dummy bilet oluşturuldu.")

if __name__ == "__main__":
    seed_dummy_data()
