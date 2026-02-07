import random
from datetime import datetime, timedelta
from backend.database import db

def seed_bulk_data():
    firma_id = 1
    servisler = db.get_servisler(firma_id)
    if not servisler:
        print("Hizmet bulunamadı.")
        return
    
    servis_ids = [s['id'] for s in servisler]
    kuyruklar = db.get_kuyruklar_by_firma(firma_id)
    kuyruk_map = {k['servis_id']: k['id'] for k in kuyruklar}

    print(f"Toplu veri üretimi başlatıldı...")

    now = datetime.now()
    start_date = now - timedelta(days=180)
    
    all_data = []
    current_date = start_date
    while current_date <= now:
        is_weekend = current_date.weekday() >= 5
        month_factor = 1.0 + 0.3 * random.uniform(-1, 1)
        daily_count = int(random.randint(15, 25) * month_factor)
        if is_weekend: daily_count = int(daily_count * 0.4)
        
        for _ in range(daily_count):
            hour = random.randint(8, 17)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            ts = current_date.replace(hour=hour, minute=minute, second=second)
            sid = random.choice(servis_ids)
            kid = kuyruk_map.get(sid)
            if not kid: continue

            rand_status = random.random()
            if rand_status < 0.8:
                durum, cagirilma, tamamlanma = 'completed', ts + timedelta(minutes=random.randint(1, 5)), ts + timedelta(minutes=random.randint(5, 20))
            elif rand_status < 0.9:
                durum, cagirilma, tamamlanma = 'waiting', None, None
            else:
                durum, cagirilma, tamamlanma = 'calling', ts + timedelta(minutes=random.randint(0, 2)), None

            all_data.append({
                "kid": kid, "sid": sid, "fid": firma_id, 
                "num": f"T{random.randint(100, 999)}",
                "onc": 1 if random.random() < 0.1 else 0,
                "dur": durum, "olust": ts, "cagir": cagirilma, "tamam": tamamlanma
            })
        current_date += timedelta(days=1)

    print(f"Toplam {len(all_data)} satır hazırlandı. Veritabanına toplu gönderiliyor...")
    
    # SQL toplu insert (Transaction verimliliği için parçalı gönderim)
    batch_size = 100
    for i in range(0, len(all_data), batch_size):
        batch = all_data[i:i + batch_size]
        # SQL construct: DB'nin kullandığı parametre yapısına göre
        # db.execute_query genelde tek tek çalışıyor ama biz döngüyle batch gönderelim.
        # Aslında her satır ayrı SQL yerine tek SQL yapmak daha hızlı. 
        # Ancak db.execute_query implementasyonunu tam bilmediğimizden (ORM/Raw), 
        # TRANSACTION bloğu olmadığı için en azından döngü hızlanacak.
        
        # Daha da hızlandırmak için VALUES (...,...), (...,...) yapalım:
        values_parts = []
        params = {}
        for idx, row in enumerate(batch):
            suffix = f"_{idx}"
            values_parts.append(f"(:kid{suffix}, :sid{suffix}, :fid{suffix}, :num{suffix}, :onc{suffix}, :dur{suffix}, :olust{suffix}, :cagir{suffix}, :tamam{suffix})")
            params.update({
                f"kid{suffix}": row['kid'], f"sid{suffix}": row['sid'], f"fid{suffix}": row['fid'],
                f"num{suffix}": row['num'], f"onc{suffix}": row['onc'], f"dur{suffix}": row['dur'],
                f"olust{suffix}": row['olust'], f"cagir{suffix}": row['cagir'], f"tamam{suffix}": row['tamam']
            })
        
        sql = f"""
            INSERT INTO siramatik.siralar 
            (kuyruk_id, servis_id, firma_id, numara, oncelik, durum, olusturulma, cagirilma, tamamlanma)
            VALUES {", ".join(values_parts)}
        """
        db.execute_query(sql, params)
        print(f"Ilerleme: %{int((i+len(batch))/len(all_data)*100)}")

    print(f"BAŞARILI! {len(all_data)} gerçekçi veri eklendi.")

if __name__ == "__main__":
    seed_bulk_data()
