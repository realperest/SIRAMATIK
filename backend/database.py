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

# Engine oluştur - search_path ile siramatik schema'yı belirt
connect_args = {"options": "-c search_path=siramatik,public"}
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
    
    def get_bekleyen_siralar(self, kuyruk_id: int) -> List[Dict]:
        """Bekleyen sıraları getir (öncelik sırasına göre)"""
        return self.execute_query("""
            SELECT * FROM siramatik.siralar 
            WHERE kuyruk_id = :kuyruk_id AND durum = 'waiting'
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
        return result[0] if result else None
    
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
    
    # --- EKRAN ---
    
    def get_son_cagrilar(self, firma_id: int, limit: int = 5) -> List[Dict]:
        """Son çağrılan sıraları getir (ekran için)"""
        return self.execute_query("""
            SELECT s.*, k.ad as kuyruk_ad, k.kod as kuyruk_kod,
                   sv.ad as servis_ad
            FROM siramatik.siralar s
            JOIN siramatik.kuyruklar k ON s.kuyruk_id = k.id
            JOIN siramatik.servisler sv ON s.servis_id = sv.id
            WHERE s.firma_id = :firma_id 
            AND s.durum IN ('calling', 'serving')
            AND s.cagirilma > (NOW() - INTERVAL '30 seconds')
            ORDER BY s.cagirilma DESC
            LIMIT :limit
        """, {"firma_id": firma_id, "limit": limit})
    
    def get_tum_bekleyen_siralar(self, firma_id: int) -> List[Dict]:
        """Firmaya ait tüm bekleyen sıraları getir"""
        return self.execute_query("""
            SELECT s.* 
            FROM siramatik.siralar s
            JOIN siramatik.kuyruklar k ON s.kuyruk_id = k.id
            JOIN siramatik.servisler sv ON k.servis_id = sv.id
            WHERE sv.firma_id = :firma_id 
            AND s.durum = 'waiting'
            ORDER BY s.oncelik DESC, s.olusturulma ASC
        """, {"prefix_removed_already_handled": None, "firma_id": firma_id})
        
    def get_kuyruklar_by_firma(self, firma_id: int) -> List[Dict]:
        """Firmaya ait tüm kuyrukları getir"""
        return self.execute_query("""
            SELECT k.*, sv.id as servis_id, sv.ad as servis_ad
            FROM siramatik.kuyruklar k
            JOIN siramatik.servisler sv ON k.servis_id = sv.id
            WHERE sv.firma_id = :firma_id
        """, {"firma_id": firma_id})

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

    # --- İSTATİSTİKLER ---

    def get_firma_istatistikleri(self, firma_id: int) -> Dict:
        """Firma genel istatistiklerini getir"""
        result = self.execute_query("""
            SELECT 
                COUNT(*) as toplam_sira,
                COUNT(*) FILTER (WHERE oncelik > 0) as vip_sira,
                COUNT(*) FILTER (WHERE durum = 'waiting') as bekleyen,
                COUNT(*) FILTER (WHERE durum = 'calling') as cagirildi,
                COUNT(*) FILTER (WHERE durum = 'completed') as tamamlandi
            FROM siramatik.siralar
            WHERE firma_id = :firma_id AND DATE(olusturulma) = CURRENT_DATE
        """, {"firma_id": firma_id})
        return result[0] if result else {}

# Global database instance
db = Database()
