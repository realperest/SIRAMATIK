"""
Sıramatik - Veritabanı Bağlantısı
SQLAlchemy ile Siramatik Schema Desteği
YAPLUS yönteminden esinlenildi
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Supabase bağlantı bilgileri
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# SQLAlchemy için PostgreSQL bağlantı URL'i
# YAPLUS yöntemi: aws-1 pooler + search_path
DB_URL = "postgresql://postgres.wyursjdrnnjabpfeucyi:qk4SEnyhu3NUk2@aws-1-eu-central-1.pooler.supabase.com:6543/postgres"

# Engine oluştur - SADECE siramatik schema
connect_args = {"options": "-c search_path=siramatik"}
engine = create_engine(DB_URL, echo=False, connect_args=connect_args)


class Database:
    """Veritabanı yöneticisi - SQLAlchemy ile siramatik schema"""
    
    def __init__(self):
        self.engine = engine
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """SQL sorgusu çalıştır"""
        with Session(self.engine) as session:
            result = session.execute(text(query), params or {})
            
            # SELECT sorguları için sonuçları döndür
            if result.returns_rows:
                columns = result.keys()
                # print(f"DEBUG SQL KEYS: {columns}") # LOG
                data = [dict(zip(columns, row)) for row in result.fetchall()]
                session.commit() # RETURNING kullanan INSERT/UPDATE için commit şart!
                return data
            
            session.commit()
            return []
    
    # --- FİRMALAR ---
    
    def get_firma(self, firma_id: int) -> Optional[Dict]:
        """Firma bilgisini getir"""
        result = self.execute_query(
            "SELECT * FROM siramatik.firmalar WHERE id = :firma_id",
            {"firma_id": firma_id}
        )
        return result[0] if result else None
    
    def get_all_firmalar(self) -> List[Dict]:
        """Tüm firmaları getir"""
        return self.execute_query("SELECT * FROM siramatik.firmalar WHERE aktif = true ORDER BY ad")
    
    # --- SERVİSLER ---
    
    def get_servisler(self, firma_id: int) -> List[Dict]:
        """Firmaya ait servisleri getir"""
        return self.execute_query(
            "SELECT * FROM siramatik.servisler WHERE firma_id = :firma_id AND aktif = true ORDER BY ad",
            {"firma_id": firma_id}
        )
    
    def get_servis(self, servis_id: int) -> Optional[Dict]:
        """Servis bilgisini getir"""
        result = self.execute_query(
            "SELECT * FROM siramatik.servisler WHERE id = :servis_id",
            {"servis_id": servis_id}
        )
        return result[0] if result else None

    def create_servis(self, firma_id: int, ad: str, kod: str, aciklama: str = None) -> Dict:
        """Yeni servis oluştur"""
        result = self.execute_query("""
            INSERT INTO siramatik.servisler (firma_id, ad, kod, aciklama)
            VALUES (:firma_id, :ad, :kod, :aciklama)
            RETURNING *
        """, {"firma_id": firma_id, "ad": ad, "kod": kod, "aciklama": aciklama})
        return result[0] if result else None

    def update_servis(self, servis_id: int, data: Dict) -> Dict:
        """Servis güncelle"""
        fields = []
        params = {"servis_id": servis_id}
        for key, value in data.items():
            fields.append(f"{key} = :{key}")
            params[key] = value
        query = f"UPDATE siramatik.servisler SET {', '.join(fields)} WHERE id = :servis_id RETURNING *"
        result = self.execute_query(query, params)
        return result[0] if result else None

    def delete_servis(self, servis_id: int) -> bool:
        """Servis sil"""
        self.execute_query("DELETE FROM siramatik.servisler WHERE id = :servis_id", {"servis_id": servis_id})
        return True
    
    # --- KUYRUKLAR ---
    
    def get_kuyruklar(self, servis_id: int) -> List[Dict]:
        """Servise ait kuyrukları getir"""
        return self.execute_query(
            "SELECT * FROM siramatik.kuyruklar WHERE servis_id = :servis_id AND aktif = true ORDER BY kod",
            {"servis_id": servis_id}
        )
    
    def get_kuyruk(self, kuyruk_id: int) -> Optional[Dict]:
        """Kuyruk bilgisini getir"""
        result = self.execute_query(
            "SELECT * FROM siramatik.kuyruklar WHERE id = :kuyruk_id",
            {"kuyruk_id": kuyruk_id}
        )
        return result[0] if result else None

    def create_kuyruk(self, servis_id: int, ad: str, kod: str, oncelik: int = 0) -> Dict:
        """Yeni kuyruk oluştur"""
        result = self.execute_query("""
            INSERT INTO siramatik.kuyruklar (servis_id, ad, kod, oncelik)
            VALUES (:servis_id, :ad, :kod, :oncelik)
            RETURNING *
        """, {"servis_id": servis_id, "ad": ad, "kod": kod, "oncelik": oncelik})
        return result[0] if result else None

    def update_kuyruk(self, kuyruk_id: int, data: Dict) -> Dict:
        """Kuyruk güncelle"""
        fields = []
        params = {"kuyruk_id": kuyruk_id}
        for key, value in data.items():
            fields.append(f"{key} = :{key}")
            params[key] = value
        query = f"UPDATE siramatik.kuyruklar SET {', '.join(fields)} WHERE id = :kuyruk_id RETURNING *"
        result = self.execute_query(query, params)
        return result[0] if result else None

    def delete_kuyruk(self, kuyruk_id: int) -> bool:
        """Kuyruk sil"""
        self.execute_query("DELETE FROM siramatik.kuyruklar WHERE id = :kuyruk_id", {"kuyruk_id": kuyruk_id})
        return True
    
    # --- SIRALAR ---
    
    def create_sira(self, kuyruk_id: int, servis_id: int, firma_id: int, 
                    oncelik: int = 0, notlar: str = None) -> Dict:
        """Yeni sıra oluştur"""
        result = self.execute_query("""
            INSERT INTO siramatik.siralar (kuyruk_id, servis_id, firma_id, oncelik, notlar, numara)
            VALUES (:kuyruk_id, :servis_id, :firma_id, :oncelik, :notlar, 
                    siramatik.yeni_sira_numarasi(:kuyruk_id, :oncelik))
            RETURNING *
        """, {
            "kuyruk_id": kuyruk_id,
            "servis_id": servis_id,
            "firma_id": firma_id,
            "oncelik": oncelik,
            "notlar": notlar
        })
        return result[0] if result else None
    
    def create_manuel_sira(self, kuyruk_id: int, servis_id: int, firma_id: int, 
                           numara: str, oncelik: int = 0, notlar: str = None) -> Dict:
        """Manuel sıra oluştur (Özel numara ile)"""
        result = self.execute_query("""
            INSERT INTO siramatik.siralar (kuyruk_id, servis_id, firma_id, oncelik, notlar, numara)
            VALUES (:kuyruk_id, :servis_id, :firma_id, :oncelik, :notlar, :numara)
            RETURNING *
        """, {
            "kuyruk_id": kuyruk_id,
            "servis_id": servis_id,
            "firma_id": firma_id,
            "oncelik": oncelik,
            "notlar": notlar,
            "numara": numara
        })
        return result[0] if result else None
    
    def get_bekleyen_siralar(self, kuyruk_id: int) -> List[Dict]:
        """Bekleyen sıraları getir (Bugünkü, öncelik sırasına göre)"""
        return self.execute_query("""
            SELECT * FROM siramatik.siralar 
            WHERE kuyruk_id = :kuyruk_id 
            AND durum = 'waiting'
            AND olusturulma::date = CURRENT_DATE
            ORDER BY oncelik DESC, olusturulma ASC
        """, {"kuyruk_id": kuyruk_id})
    
    def cagir_sira(self, sira_id: int, kullanici_id: int, konum: str = None) -> Dict:
        """Sırayı çağır"""
        result = self.execute_query("""
            UPDATE siramatik.siralar 
            SET durum = 'calling', 
                cagiran_kullanici_id = :kullanici_id,
                konum = :konum,
                cagirilma = NOW()
            WHERE id = :sira_id
            RETURNING *
        """, {
            "sira_id": sira_id,
            "kullanici_id": kullanici_id,
            "konum": konum
        })
        return result[0] if result else None
    
    def tamamla_sira(self, sira_id: int) -> Dict:
        """Sırayı tamamla"""
        result = self.execute_query("""
            UPDATE siramatik.siralar 
            SET durum = 'completed', tamamlanma = NOW()
            WHERE id = :sira_id
            RETURNING *
        """, {"sira_id": sira_id})
    
    def get_son_cagrilar(self, firma_id: Any, limit: int = 5, servis_id: int = None) -> List[Dict]:
        """Ekran için son çağrıları getir"""
        query = """
            SELECT 
                s.*, 
                ser.ad as servis_ad,
                k.ad as kuyruk_ad
            FROM siramatik.siralar s
            LEFT JOIN siramatik.servisler ser ON s.servis_id = ser.id
            LEFT JOIN siramatik.kuyruklar k ON s.kuyruk_id = k.id
            WHERE s.firma_id = :firma_id 
            AND s.durum = 'calling'
            AND s.cagirilma > (NOW() - INTERVAL '60 seconds')
        """
        params = {"firma_id": firma_id, "limit": limit}

        if servis_id:
            query += " AND s.servis_id = :servis_id"
            params["servis_id"] = servis_id
            
        query += " ORDER BY s.cagirilma DESC NULLS LAST LIMIT :limit"
        
        return self.execute_query(query, params)
    
    # --- KULLANICILAR ---
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Email ile kullanıcı bul"""
        result = self.execute_query(
            "SELECT * FROM siramatik.kullanicilar WHERE email = :email",
            {"email": email}
        )
        return result[0] if result else None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """ID ile kullanıcı bul"""
        result = self.execute_query(
            "SELECT * FROM siramatik.kullanicilar WHERE id = :user_id",
            {"user_id": user_id}
        )
        return result[0] if result else None
    
    def create_user(self, email: str, ad_soyad: str, sifre_hash: str, 
                    firma_id: int, rol: str = 'staff') -> Dict:
        """Yeni kullanıcı oluştur"""
        result = self.execute_query("""
            INSERT INTO siramatik.kullanicilar (email, ad_soyad, sifre_hash, firma_id, rol)
            VALUES (:email, :ad_soyad, :sifre_hash, :firma_id, :rol)
            RETURNING *
        """, {
            "email": email,
            "ad_soyad": ad_soyad,
            "sifre_hash": sifre_hash,
            "firma_id": firma_id,
            "rol": rol
        })
        return result[0] if result else None
    

    
    def get_tum_bekleyen_siralar(self, firma_id: int) -> List[Dict]:
        """Firmaya ait tüm bekleyen sıraları getir"""
        return self.execute_query("""
            SELECT s.* 
            FROM siramatik.siralar s
            JOIN siramatik.kuyruklar k ON s.kuyruk_id = k.id
            JOIN siramatik.servisler sv ON k.servis_id = sv.id
            WHERE sv.firma_id = :firma_id 
            AND s.durum = 'waiting'
            AND s.olusturulma::date = CURRENT_DATE
            ORDER BY s.oncelik DESC, s.olusturulma ASC
        """, {"prefix_removed_already_handled": None, "firma_id": firma_id})
        
    def get_gunluk_istatistik(self, firma_id: str, kullanici_id: Optional[str] = None) -> Dict:
        """Günlük istatistikleri getir"""
        
        # Personel bazlı toplam (Eğer kullanici_id varsa)
        parametreler = {"firma_id": firma_id}
        
        sql_toplam = """
            SELECT COUNT(*) as sayi 
            FROM siramatik.siralar s
            JOIN siramatik.kuyruklar k ON s.kuyruk_id = k.id
            JOIN siramatik.servisler sv ON k.servis_id = sv.id
            WHERE sv.firma_id = :firma_id 
            AND s.olusturulma::date = CURRENT_DATE
        """
        
        if kullanici_id:
            sql_toplam += " AND s.cagiran_kullanici_id = :kullanici_id"
            parametreler["kullanici_id"] = kullanici_id
            
        res_toplam = self.execute_query(sql_toplam, parametreler)
        
        # Bekleyen (Firma geneli)
        res_bekleyen = self.execute_query("""
            SELECT COUNT(*) as sayi 
            FROM siramatik.siralar s
            JOIN siramatik.kuyruklar k ON s.kuyruk_id = k.id
            JOIN siramatik.servisler sv ON k.servis_id = sv.id
            WHERE sv.firma_id = :firma_id 
            AND s.durum = 'waiting'
            AND s.olusturulma::date = CURRENT_DATE
        """, {"firma_id": firma_id})
        
        return {
            "toplam": res_toplam[0]['sayi'] if res_toplam else 0,
            "bekleyen": res_bekleyen[0]['sayi'] if res_bekleyen else 0
        }
        
    def get_kuyruklar_by_firma(self, firma_id: int) -> List[Dict]:
        """Firmaya ait tüm kuyrukları getir"""
        return self.execute_query("""
            SELECT k.*, sv.id as servis_id, sv.ad as servis_ad
            FROM siramatik.kuyruklar k
            JOIN siramatik.servisler sv ON k.servis_id = sv.id
            WHERE sv.firma_id = :firma_id
        """, {"firma_id": firma_id})
        
    def get_servisler_by_firma(self, firma_id: str) -> List[Dict]:
        """Firmaya ait servisleri getir"""
        return self.execute_query("""
            SELECT * FROM siramatik.servisler WHERE firma_id = :firma_id ORDER BY ad
        """, {"firma_id": firma_id})
        
    def create_servis(self, firma_id: int, ad: str, kod: str = None, aciklama: str = None) -> Dict:
        """Yeni servis oluştur"""
        res = self.execute_query("""
            INSERT INTO siramatik.servisler (firma_id, ad, kod, aciklama, aktif)
            VALUES (:firma_id, :ad, :kod, :aciklama, TRUE)
            RETURNING *
        """, {"firma_id": firma_id, "ad": ad, "kod": kod, "aciklama": aciklama})
        return res[0] if res else None

    def update_user_servis(self, user_id: str, servis_id: Optional[int]) -> bool:
        """Kullanıcının sorumlu olduğu servisi güncelle"""
        self.execute_query("""
            UPDATE siramatik.kullanicilar SET servis_id = :servis_id WHERE id = :user_id
        """, {"user_id": user_id, "servis_id": servis_id})
        return True


    # --- CİHAZLAR ---

    def get_cihazlar(self, firma_id: int) -> List[Dict]:
        """Firmaya ait tüm cihazları getir"""
        return self.execute_query("""
            SELECT c.*, s.ad as servis_ad, k.ad as kuyruk_ad
            FROM siramatik.cihazlar c
            LEFT JOIN siramatik.servisler s ON c.servis_id = s.id
            LEFT JOIN siramatik.kuyruklar k ON c.kuyruk_id = k.id
            WHERE c.firma_id = :firma_id
            ORDER BY c.tip, c.ad
        """, {"firma_id": firma_id})

    def get_cihaz(self, cihaz_id: int) -> Optional[Dict]:
        """Cihaz bilgisini getir"""
        result = self.execute_query(
            "SELECT * FROM siramatik.cihazlar WHERE id = :cihaz_id",
            {"cihaz_id": cihaz_id}
        )
        return result[0] if result else None

    def update_cihaz(self, cihaz_id: int, data: Dict) -> Dict:
        """Cihaz bilgilerini güncelle"""
        # Dinamik SQL oluştur
        fields = []
        params = {"cihaz_id": cihaz_id}
        for key, value in data.items():
            if value is not None:
                fields.append(f"{key} = :{key}")
                params[key] = value
        
        if not fields:
            return self.get_cihaz(cihaz_id)

        query = f"UPDATE siramatik.cihazlar SET {', '.join(fields)} WHERE id = :cihaz_id RETURNING *"
        result = self.execute_query(query, params)
        return result[0] if result else None

    def cihaz_bildir(self, firma_id: int, ad: str, tip: str, mac: str = None) -> Dict:
        """Cihazın aktif olduğunu bildir (Upsert)"""
        # MAC adresi yoksa Ad üzerinden eşle
        result = self.execute_query("""
            INSERT INTO siramatik.cihazlar (firma_id, ad, tip, mac_adresi, aktif, son_gorunme)
            VALUES (:firma_id, :ad, :tip, :mac, TRUE, NOW())
            ON CONFLICT (firma_id, mac_adresi) DO UPDATE 
            SET aktif = TRUE, son_gorunme = NOW(), tip = :tip
            RETURNING *
        """, {"firma_id": firma_id, "ad": ad, "tip": tip, "mac": mac or ad})
        return result[0] if result else None

    # --- İSTATİSTİKLER ---

    def get_firma_istatistikleri(self, firma_id: int, servis_id: Optional[int] = None, 
                                 period_type: str = "hour", time_range: str = "today",
                                 start_date: str = None, end_date: str = None) -> Dict:
        """Firma istatistiklerini getir (Gelişmiş Zaman ve Periyot Filtreli)"""
        params = {"firma_id": firma_id}
        
        # 1. ZAMAN FİLTRESİ OLUŞTUR
        time_filter = ""
        if time_range == "today":
            time_filter = " AND DATE(s.olusturulma) = CURRENT_DATE"
        elif time_range == "this_week":
            time_filter = " AND s.olusturulma >= date_trunc('week', CURRENT_DATE)"
        elif time_range == "this_month":
            time_filter = " AND s.olusturulma >= date_trunc('month', CURRENT_DATE)"
        elif time_range == "this_year":
            time_filter = " AND s.olusturulma >= date_trunc('year', CURRENT_DATE)"
        elif time_range == "all_time":
            time_filter = "" # Filtre uygulama
        elif time_range == "custom" and start_date:
            time_filter = " AND s.olusturulma::date BETWEEN :start AND :end"
            params["start"] = start_date
            params["end"] = end_date or start_date
        
        # 2. SERVİS FİLTRESİ
        service_filter = ""
        if servis_id:
            service_filter = " AND s.servis_id = :servis_id"
            params["servis_id"] = servis_id

        # 3. TEMEL SAYILAR (Kartlar için)
        base_stats = self.execute_query(f"""
            SELECT 
                COUNT(*) as toplam_sira,
                COUNT(*) FILTER (WHERE oncelik > 0) as vip_sira,
                COUNT(*) FILTER (WHERE durum = 'waiting') as bekleyen,
                COUNT(*) FILTER (WHERE durum = 'calling') as cagirildi,
                COUNT(*) FILTER (WHERE durum = 'completed') as tamamlandi,
                AVG(CASE WHEN durum = 'completed' THEN EXTRACT(EPOCH FROM (cagirilma - olusturulma))/60 END) as ort_bekleme_dk,
                AVG(CASE WHEN durum = 'completed' THEN EXTRACT(EPOCH FROM (tamamlanma - cagirilma))/60 END) as ort_islem_dk
            FROM siramatik.siralar s
            WHERE s.firma_id = :firma_id {time_filter} {service_filter}
        """, params)[0]

        # 4. PERİYOT GRUPLAMA (Grafik için)
        group_sql = ""
        label_format = ""
        if period_type == "hour":
            group_sql = "EXTRACT(HOUR FROM s.olusturulma)"
            label_format = "saat"
        elif period_type == "weekday":
            group_sql = "EXTRACT(DOW FROM s.olusturulma)"
            label_format = "gün" # 0: Pazar, 1: Pazartesi...
        elif period_type == "monthday":
            group_sql = "EXTRACT(DAY FROM s.olusturulma)"
            label_format = "gün"
        elif period_type == "week":
            group_sql = "EXTRACT(WEEK FROM s.olusturulma)"
            label_format = "hafta"
        elif period_type == "month":
            group_sql = "EXTRACT(MONTH FROM s.olusturulma)"
            label_format = "ay"
        else:
            group_sql = "EXTRACT(HOUR FROM s.olusturulma)"
            label_format = "saat"

        periodic_raw = self.execute_query(f"""
            SELECT {group_sql} as label, COUNT(*) as adet
            FROM siramatik.siralar s
            WHERE s.firma_id = :firma_id {time_filter} {service_filter}
            GROUP BY label ORDER BY label
        """, params)

        # Label'ları insan diline çevir
        labels = []
        data = []
        
        day_names = ["Paz", "Pzt", "Sal", "Çar", "Per", "Cum", "Cmt"]
        month_names = ["", "Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]

        for item in periodic_raw:
            val = int(item['label'])
            if period_type == "weekday":
                labels.append(day_names[val])
            elif period_type == "month":
                labels.append(month_names[val])
            elif period_type == "hour":
                labels.append(f"{val:02d}:00")
            elif period_type == "week":
                labels.append(f"{val}. Hafta")
            else:
                labels.append(str(val))
            data.append(item['adet'])

        # 5. SERVİS DAĞILIMI
        service_stats = self.execute_query(f"""
            SELECT ser.ad, COUNT(s.id) as adet
            FROM siramatik.servisler ser
            LEFT JOIN siramatik.siralar s ON ser.id = s.servis_id {time_filter}
            WHERE ser.firma_id = :firma_id {" AND ser.id = :servis_id" if servis_id else ""}
            GROUP BY ser.ad
        """, params)

        # 6. SON BİLETLER
        recent_tickets = self.execute_query(f"""
            SELECT s.id, s.numara, s.durum, to_char(s.olusturulma, 'DD.MM HH24:MI') as saat, ser.ad as servis_ad
            FROM siramatik.siralar s
            JOIN siramatik.servisler ser ON s.servis_id = ser.id
            WHERE s.firma_id = :firma_id {time_filter} {service_filter}
            ORDER BY s.olusturulma DESC LIMIT 10
        """, params)

        return {
            **base_stats,
            "hourly_labels": labels, # Frontend uyumu için aynı keyler
            "hourly_data": data,
            "service_labels": [s['ad'] for s in service_stats if s['adet'] > 0],
            "service_data": [s['adet'] for s in service_stats if s['adet'] > 0],
            "recent_tickets": recent_tickets
        }

# Global database instance
db = Database()
