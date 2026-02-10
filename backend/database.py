"""
Sıramatik - Veritabanı Bağlantısı
SQLAlchemy ile Siramatik Schema Desteği
YAPLUS yönteminden esinlenildi
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
import os
import json
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# PostgreSQL Bağlantı URL'i (Supabase)
# Not: production ortamında connection pooling kullanılmalı
DB_URL = "postgresql://postgres.wyursjdrnnjabpfeucyi:qk4SEnyhu3NUk2@aws-1-eu-central-1.pooler.supabase.com:6543/postgres"

# Engine oluştur - search_path ile siramatik schema'yı belirt
# Engine oluştur - search_path ile siramatik schema'yı belirt
connect_args = {
    "options": "-c search_path=siramatik,public",
    "keepalives": 1,
    "keepalives_idle": 30,
    "keepalives_interval": 10,
    "keepalives_count": 5
}

engine = create_engine(
    DB_URL, 
    echo=False, 
    pool_size=5, 
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    connect_args=connect_args
)


class Database:
    """Veritabanı yöneticisi - SQLAlchemy ile siramatik schema"""
    
    def __init__(self):
        self.engine = engine
        self.init_tables()
    
    def init_tables(self):
        """Eksik tabloları oluştur ve kolonları güncelle (Optimize Edildi)"""
        with Session(self.engine) as session:
            # 1. Ana Tabloları Oluştur
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS siramatik.kuyruk_konumlar (
                    id SERIAL PRIMARY KEY,
                    kuyruk_id INTEGER REFERENCES siramatik.kuyruklar(id) ON DELETE CASCADE,
                    ad VARCHAR(50) NOT NULL,
                    aciklama TEXT,
                    aktif BOOLEAN DEFAULT TRUE,
                    olusturulma TIMESTAMP DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS siramatik.cihazlar (
                    id SERIAL PRIMARY KEY,
                    firma_id INTEGER REFERENCES siramatik.firmalar(id) ON DELETE CASCADE,
                    konum_id INTEGER REFERENCES siramatik.kuyruk_konumlar(id) ON DELETE SET NULL,
                    ad VARCHAR(100),
                    tip VARCHAR(20),
                    mac VARCHAR(20),
                    ip VARCHAR(20),
                    metadata JSONB DEFAULT '{}',
                    aktif BOOLEAN DEFAULT TRUE,
                    son_gorulme TIMESTAMP DEFAULT NOW(),
                    olusturulma TIMESTAMP DEFAULT NOW()
                );
            """))
            session.commit()

            # 2. Kolon Güncellemeleri (Toplu Try-Except bloğu yerine tek tek ama aynı bağlantıda)
            alter_queries = [
                "ALTER TABLE siramatik.firmalar ADD COLUMN IF NOT EXISTS sifre_kilitli BOOLEAN DEFAULT FALSE",
                "ALTER TABLE siramatik.firmalar ADD COLUMN IF NOT EXISTS sozlesme_bitis TIMESTAMP DEFAULT (NOW() + INTERVAL '1 year')",
                "ALTER TABLE siramatik.firmalar ADD COLUMN IF NOT EXISTS lisans_tipi VARCHAR(20) DEFAULT 'Kiralama'",
                "ALTER TABLE siramatik.firmalar ADD COLUMN IF NOT EXISTS max_cihaz INTEGER DEFAULT 10",
                "ALTER TABLE siramatik.firmalar ADD COLUMN IF NOT EXISTS notlar TEXT",
                "ALTER TABLE siramatik.kullanicilar ADD COLUMN IF NOT EXISTS varsayilan_kuyruk_id INTEGER REFERENCES siramatik.kuyruklar(id) ON DELETE SET NULL",
                "ALTER TABLE siramatik.kullanicilar ADD COLUMN IF NOT EXISTS varsayilan_konum_id INTEGER REFERENCES siramatik.kuyruk_konumlar(id) ON DELETE SET NULL",
                "ALTER TABLE siramatik.kullanicilar ADD COLUMN IF NOT EXISTS servis_ids INTEGER[]",
                "ALTER TABLE siramatik.kullanicilar ADD COLUMN IF NOT EXISTS kuyruk_ids INTEGER[]",
                "ALTER TABLE siramatik.kullanicilar ADD COLUMN IF NOT EXISTS durum VARCHAR(20) DEFAULT 'available'",
                "ALTER TABLE siramatik.kullanicilar ADD COLUMN IF NOT EXISTS mola_baslangic TIMESTAMP",
                "ALTER TABLE siramatik.kullanicilar ADD COLUMN IF NOT EXISTS mola_nedeni VARCHAR(50)",
                "ALTER TABLE siramatik.siralar ADD COLUMN IF NOT EXISTS islem_baslangic TIMESTAMP",
                "ALTER TABLE siramatik.siralar ADD COLUMN IF NOT EXISTS tamamlanma TIMESTAMP",
                "ALTER TABLE siramatik.siralar ADD COLUMN IF NOT EXISTS cagirilma_sayisi INTEGER DEFAULT 1",
                "ALTER TABLE siramatik.siralar ADD COLUMN IF NOT EXISTS notlar TEXT"
            ]

            for q in alter_queries:
                try:
                    # PostgreSQL 9.6+ supports IF NOT EXISTS for columns, but we use generic approach or catch error
                    # Supabase is Postgres 15+, so IF NOT EXISTS works!
                    session.execute(text(q))
                    session.commit()
                except Exception as e:
                    session.rollback()
                    # IF NOT EXISTS desteklenmiyorsa veya başka hata varsa yut (Eski yöntem gibi)
                    # print(f"Migration Log: {e}") 
                    pass
    
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

    def create_firma(self, data: Dict) -> Dict:
        """Yeni firma oluştur"""
        result = self.execute_query("""
            INSERT INTO siramatik.firmalar (ad, sektor, ekran_sifre, aktif, sifre_kilitli, sozlesme_bitis, lisans_tipi, max_cihaz, notlar)
            VALUES (:ad, :sektor, :ekran_sifre, :aktif, :sifre_kilitli, :sozlesme_bitis, :lisans_tipi, :max_cihaz, :notlar)
            RETURNING *
        """, {
            "ad": data.get("ad"),
            "sektor": data.get("sektor"),
            "ekran_sifre": data.get("ekran_sifre", "153624"),
            "aktif": data.get("aktif", True),
            "sifre_kilitli": data.get("sifre_kilitli", False),
            "sozlesme_bitis": data.get("sozlesme_bitis"),
            "lisans_tipi": data.get("lisans_tipi", "Kiralama"),
            "max_cihaz": data.get("max_cihaz", 10),
            "notlar": data.get("notlar", "")
        })
        return result[0] if result else None

    def update_firma(self, firma_id: int, data: Dict) -> Dict:
        """Firma bilgilerini güncelle (Örn: ekran_sifre)"""
        fields = []
        params = {"firma_id": firma_id}
        for key, value in data.items():
            fields.append(f"{key} = :{key}")
            params[key] = value
        query = f"UPDATE siramatik.firmalar SET {', '.join(fields)} WHERE id = :firma_id RETURNING *"
        result = self.execute_query(query, params)
        return result[0] if result else None

    def get_firma_by_ekran_sifre(self, sifre: str) -> Optional[Dict]:
        """Ekran müdahale şifresi ile firma bul"""
        result = self.execute_query(
            "SELECT * FROM siramatik.firmalar WHERE ekran_sifre = :sifre AND aktif = true",
            {"sifre": sifre}
        )
        return result[0] if result else None
    
    # --- SERVİSLER ---
    
    def get_servisler(self, firma_id: int) -> List[Dict]:
        """Firmaya ait servisleri getir (Kuyruk sayıları ile birlikte)"""
        return self.execute_query("""
            SELECT s.*, 
                   (SELECT COUNT(*) FROM siramatik.kuyruklar k WHERE k.servis_id = s.id AND k.aktif = true) as kuyruk_sayisi
            FROM siramatik.servisler s 
            WHERE s.firma_id = :firma_id AND s.aktif = true 
            ORDER BY s.ad
        """, {"firma_id": firma_id})
    
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
        """Servise ait kuyrukları getir (Bekleyen sayıları ile birlikte)"""
        queues = self.execute_query("""
            SELECT k.*, 
                   (SELECT COUNT(*) FROM siramatik.siralar s 
                    WHERE s.kuyruk_id = k.id AND s.durum = 'waiting' 
                    AND (s.olusturulma AT TIME ZONE 'Europe/Istanbul')::date = (NOW() AT TIME ZONE 'Europe/Istanbul')::date
                   ) as bekleyen_sayisi
            FROM siramatik.kuyruklar k 
            WHERE k.servis_id = :servis_id AND k.aktif = true 
            ORDER BY k.oncelik DESC, k.kod
        """, {"servis_id": servis_id})
        
        if not queues:
            return []
            
        # Toplu konum çekme (N+1 engelleme)
        kuyruk_ids = [q['id'] for q in queues]
        ids_str = ",".join(str(int(i)) for i in kuyruk_ids)
        all_konumlar = self.execute_query(f"""
            SELECT id, ad, aciklama, kuyruk_id 
            FROM siramatik.kuyruk_konumlar 
            WHERE kuyruk_id IN ({ids_str})
            ORDER BY id
        """)
        
        # Eşleştirme
        for q in queues:
            q['konumlar'] = [kn for kn in all_konumlar if kn['kuyruk_id'] == q['id']]
            
        return queues
    
    def get_kuyruk(self, kuyruk_id: int) -> Optional[Dict]:
        """Kuyruk bilgisini getir"""
        result = self.execute_query(
            "SELECT * FROM siramatik.kuyruklar WHERE id = :kuyruk_id",
            {"kuyruk_id": kuyruk_id}
        )
        if not result: return None
        
        q = result[0]
        q['konumlar'] = self.execute_query(
            "SELECT id, ad, aciklama FROM siramatik.kuyruk_konumlar WHERE kuyruk_id = :kid ORDER BY id",
            {"kid": kuyruk_id}
        )
        return q

    def upsert_konumlar(self, kuyruk_id: int, konumlar: List[Dict]):
        """Kuyruk konumlarını güncelle (Sil ve yeniden ekle)"""
        # Önce eskileri sil
        self.execute_query("DELETE FROM siramatik.kuyruk_konumlar WHERE kuyruk_id = :kid", {"kid": kuyruk_id})
        
        # Yenileri ekle
        if konumlar:
            for loc in konumlar:
                self.execute_query("""
                    INSERT INTO siramatik.kuyruk_konumlar (kuyruk_id, ad, aciklama)
                    VALUES (:kid, :ad, :aciklama)
                """, {"kid": kuyruk_id, "ad": loc.get('ad'), "aciklama": loc.get('aciklama')})

    def create_kuyruk(self, servis_id: int, ad: str, kod: str, oncelik: int = 0, konumlar: List[Dict] = []) -> Dict:
        """Yeni kuyruk oluştur"""
        result = self.execute_query("""
            INSERT INTO siramatik.kuyruklar (servis_id, ad, kod, oncelik)
            VALUES (:servis_id, :ad, :kod, :oncelik)
            RETURNING *
        """, {"servis_id": servis_id, "ad": ad, "kod": kod, "oncelik": oncelik})
        
        q = result[0] if result else None
        if not q: return None

        # Konumları ekle
        if konumlar:
            self.upsert_konumlar(q['id'], konumlar)
            q['konumlar'] = konumlar
            
        return q

    def update_kuyruk(self, kuyruk_id: int, data: Dict) -> Dict:
        """Kuyruk güncelle"""
        konumlar = data.pop('konumlar', None) # Data'dan ayır

        fields = []
        params = {"kuyruk_id": kuyruk_id}
        for key, value in data.items():
            fields.append(f"{key} = :{key}")
            params[key] = value
        
        if fields:
            query = f"UPDATE siramatik.kuyruklar SET {', '.join(fields)} WHERE id = :kuyruk_id RETURNING *"
            result = self.execute_query(query, params)
        
        # Konumları güncelle
        if konumlar is not None:
             self.upsert_konumlar(kuyruk_id, konumlar)

        return self.get_kuyruk(kuyruk_id)

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
            AND (olusturulma AT TIME ZONE 'Europe/Istanbul')::date = (NOW() AT TIME ZONE 'Europe/Istanbul')::date
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

    def get_active_sira_by_user(self, user_id: int) -> Optional[Dict]:
        """Kullanıcının üzerindeki aktif sırayı getir (calling veya serving)"""
        result = self.execute_query("""
            SELECT s.*, k.ad as kuyruk_ad, ser.ad as servis_ad
            FROM siramatik.siralar s
            LEFT JOIN siramatik.kuyruklar k ON s.kuyruk_id = k.id
            LEFT JOIN siramatik.servisler ser ON s.servis_id = ser.id
            WHERE s.cagiran_kullanici_id = :user_id 
            AND s.durum IN ('calling', 'serving')
            ORDER BY s.cagirilma DESC 
            LIMIT 1
        """, {"user_id": user_id})
        return result[0] if result else None

    def islem_baslat(self, sira_id: int) -> Dict:
        """Sıra işlemini başlat (Müşteri geldi)"""
        result = self.execute_query("""
            UPDATE siramatik.siralar 
            SET durum = 'serving', islem_baslangic = NOW()
            WHERE id = :sira_id
            RETURNING *
        """, {"sira_id": sira_id})
        return result[0] if result else None

    def tekrar_cagir(self, sira_id: int) -> Dict:
        """Sırayı tekrar çağır (TV'de flaşlat)"""
        result = self.execute_query("""
            UPDATE siramatik.siralar 
            SET cagirilma = NOW(), cagirilma_sayisi = cagirilma_sayisi + 1
            WHERE id = :sira_id
            RETURNING *
        """, {"sira_id": sira_id})
        return result[0] if result else None

    def gelmedi_sira(self, sira_id: int) -> Dict:
        """Sırayı gelmedi olarak işaretle"""
        result = self.execute_query("""
            UPDATE siramatik.siralar 
            SET durum = 'skipped', tamamlanma = NOW()
            WHERE id = :sira_id
            RETURNING *
        """, {"sira_id": sira_id})
        return result[0] if result else None

    def transfer_sira(self, sira_id: int, yeni_kuyruk_id: int, yeni_servis_id: int = None) -> Dict:
        """Sırayı başka kuyruğa transfer et"""
        # Önce mevcut bilet bilgisini al (oncelik vb korumak için?)
        # Ama şimdilik sadece update
        query = "UPDATE siramatik.siralar SET kuyruk_id = :yid, durum = 'waiting', cagirilma = NULL, cagiran_kullanici_id = NULL"
        params = {"sira_id": sira_id, "yid": yeni_kuyruk_id}
        if yeni_servis_id:
            query += ", servis_id = :sid"
            params["sid"] = yeni_servis_id
        query += " WHERE id = :sira_id RETURNING *"
        
        result = self.execute_query(query, params)
        return result[0] if result else None

    def update_user_status(self, user_id: int, durum: str, mola_nedeni: str = None) -> Dict:
        """Kullanıcı durumunu güncelle (Mola sistemi)"""
        mola_baslangic = "NOW()" if durum != 'available' else "NULL"
        result = self.execute_query(f"""
            UPDATE siramatik.kullanicilar 
            SET durum = :durum, 
                mola_nedeni = :mola_nedeni,
                mola_baslangic = {mola_baslangic}
            WHERE id = :user_id
            RETURNING *
        """, {"user_id": user_id, "durum": durum, "mola_nedeni": mola_nedeni})
        return result[0] if result else None

    def update_sira_notlar(self, sira_id: int, notlar: str) -> Dict:
        """Sıra notunu güncelle"""
        result = self.execute_query("""
            UPDATE siramatik.siralar 
            SET notlar = :notlar 
            WHERE id = :sira_id 
            RETURNING *
        """, {"sira_id": sira_id, "notlar": notlar})
        return result[0] if result else None
    
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
            AND (s.olusturulma AT TIME ZONE 'Europe/Istanbul')::date = (NOW() AT TIME ZONE 'Europe/Istanbul')::date
            AND s.cagirilma > (NOW() - INTERVAL '20 minutes')
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
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Kullanıcı adı ile kullanıcı bul"""
        result = self.execute_query(
            "SELECT * FROM siramatik.kullanicilar WHERE kullanici_adi = :username",
            {"username": username}
        )
        return result[0] if result else None

    def find_user_by_login(self, login: str) -> Optional[Dict]:
        """Email VEYA Kullanıcı adı ile kullanıcı bul (Giriş için)"""
        result = self.execute_query("""
            SELECT * FROM siramatik.kullanicilar 
            WHERE email = :login OR kullanici_adi = :login
        """, {"login": login})
        return result[0] if result else None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """ID ile kullanıcı bul"""
        result = self.execute_query(
            "SELECT * FROM siramatik.kullanicilar WHERE id = :user_id",
            {"user_id": user_id}
        )
        return result[0] if result else None
    
    def create_user(self, email: Optional[str], ad_soyad: str, sifre_hash: str, 
                    firma_id: Optional[int], rol: str = 'staff', servis_id: int = None, 
                    varsayilan_kuyruk_id: int = None, varsayilan_konum_id: int = None,
                    aktif: bool = True, kullanici_adi: str = None, ekran_ismi: str = None,
                    servis_ids: List[int] = None, kuyruk_ids: List[int] = None) -> Dict:
        """Yeni kullanıcı oluştur"""
        # Ekran ismi yoksa ad_soyad kullan
        if not ekran_ismi:
            ekran_ismi = ad_soyad
            
        result = self.execute_query("""
            INSERT INTO siramatik.kullanicilar (email, ad_soyad, sifre_hash, firma_id, rol, servis_id, varsayilan_kuyruk_id, varsayilan_konum_id, aktif, kullanici_adi, ekran_ismi, servis_ids, kuyruk_ids)
            VALUES (:email, :ad_soyad, :sifre_hash, :firma_id, :rol, :servis_id, :varsayilan_kuyruk_id, :varsayilan_konum_id, :aktif, :kullanici_adi, :ekran_ismi, :servis_ids, :kuyruk_ids)
            RETURNING *
        """, {
            "email": email,
            "ad_soyad": ad_soyad,
            "sifre_hash": sifre_hash,
            "firma_id": firma_id,
            "rol": rol,
            "servis_id": servis_id,
            "varsayilan_kuyruk_id": varsayilan_kuyruk_id,
            "varsayilan_konum_id": varsayilan_konum_id,
            "aktif": aktif,
            "kullanici_adi": kullanici_adi,
            "ekran_ismi": ekran_ismi,
            "servis_ids": servis_ids,
            "kuyruk_ids": kuyruk_ids
        })
        return result[0] if result else None

    def update_user(self, user_id: int, data: Dict) -> Dict:
        """Kullanıcı bilgilerini güncelle"""
        fields = []
        params = {"user_id": user_id}
        for key, value in data.items():
            fields.append(f"{key} = :{key}")
            params[key] = value
        
        if not fields:
            return self.get_user_by_id(user_id)
            
        query = f"UPDATE siramatik.kullanicilar SET {', '.join(fields)} WHERE id = :user_id RETURNING *"
        result = self.execute_query(query, params)
        return result[0] if result else None

    def delete_user(self, user_id: int) -> bool:
        """Kullanıcıyı sil"""
        self.execute_query("DELETE FROM siramatik.kullanicilar WHERE id = :user_id", {"user_id": user_id})
        return True
    

    
    def get_tum_bekleyen_siralar(self, firma_id: int) -> List[Dict]:
        """Firmaya ait tüm bekleyen sıraları getir"""
        return self.execute_query("""
            SELECT s.* 
            FROM siramatik.siralar s
            JOIN siramatik.kuyruklar k ON s.kuyruk_id = k.id
            JOIN siramatik.servisler sv ON k.servis_id = sv.id
            WHERE sv.firma_id = :firma_id 
            AND s.durum = 'waiting'
            AND (s.olusturulma AT TIME ZONE 'Europe/Istanbul')::date = (NOW() AT TIME ZONE 'Europe/Istanbul')::date
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
            AND (s.olusturulma AT TIME ZONE 'Europe/Istanbul')::date = (NOW() AT TIME ZONE 'Europe/Istanbul')::date
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
            AND (s.olusturulma AT TIME ZONE 'Europe/Istanbul')::date = (NOW() AT TIME ZONE 'Europe/Istanbul')::date
        """, {"firma_id": firma_id})
        
        # Ortalama İşlem Süresi (Bugün, Tamamlananlar)
        sql_avg = """
            SELECT AVG(EXTRACT(EPOCH FROM (tamamlanma - COALESCE(islem_baslangic, cagirilma)))) / 60 as ort_dk
            FROM siramatik.siralar s
            JOIN siramatik.kuyruklar k ON s.kuyruk_id = k.id
            JOIN siramatik.servisler sv ON k.servis_id = sv.id
            WHERE sv.firma_id = :firma_id 
            AND s.durum = 'completed'
            AND s.tamamlanma IS NOT NULL
            AND (s.olusturulma AT TIME ZONE 'Europe/Istanbul')::date = (NOW() AT TIME ZONE 'Europe/Istanbul')::date
        """
        if kullanici_id:
            sql_avg += " AND s.cagiran_kullanici_id = :kullanici_id"

        res_avg = self.execute_query(sql_avg, parametreler)
        
        return {
            "toplam": res_toplam[0]['sayi'] if res_toplam else 0,
            "bekleyen": res_bekleyen[0]['sayi'] if res_bekleyen else 0,
            "ort_islem_dk": res_avg[0]['ort_dk'] if res_avg and res_avg[0]['ort_dk'] else 0
        }
        
    def get_kuyruklar_by_firma(self, firma_id: int) -> List[Dict]:
        """Firmaya ait tüm kuyrukları getir (Bekleyen sayıları ile birlikte)"""
        queues = self.execute_query("""
            SELECT k.*, sv.ad as servis_ad,
                   (SELECT COUNT(*) FROM siramatik.siralar s 
                    WHERE s.kuyruk_id = k.id AND s.durum = 'waiting' 
                    AND (s.olusturulma AT TIME ZONE 'Europe/Istanbul')::date = (NOW() AT TIME ZONE 'Europe/Istanbul')::date
                   ) as bekleyen_sayisi
            FROM siramatik.kuyruklar k
            JOIN siramatik.servisler sv ON k.servis_id = sv.id
            WHERE sv.firma_id = :firma_id
            ORDER BY k.oncelik DESC, k.kod
        """, {"firma_id": int(firma_id)})
        
        if not queues:
            return []
            
        # Toplu konum çekme (N+1 engelleme)
        kuyruk_ids = [q['id'] for q in queues]
        ids_str = ",".join(str(int(i)) for i in kuyruk_ids)
        all_konumlar = self.execute_query(f"""
            SELECT id, ad, aciklama, kuyruk_id 
            FROM siramatik.kuyruk_konumlar 
            WHERE kuyruk_id IN ({ids_str})
            ORDER BY id
        """)
        
        # Eşleştirme
        for q in queues:
            q['konumlar'] = [kn for kn in all_konumlar if kn['kuyruk_id'] == q['id']]
            
        return queues
        
    def get_servisler_by_firma(self, firma_id: str) -> List[Dict]:
        """Firmaya ait servisleri getir (Kuyruk sayıları ile birlikte)"""
        return self.execute_query("""
            SELECT s.*, 
                   (SELECT COUNT(*) FROM siramatik.kuyruklar k WHERE k.servis_id = s.id AND k.aktif = true) as kuyruk_sayisi
            FROM siramatik.servisler s 
            WHERE s.firma_id = :firma_id 
            ORDER BY s.ad
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

    def cihaz_bildir(self, firma_id: int, ad: str, tip: str, mac: str = None, metadata: dict = {}) -> Dict:
        """Cihazın aktif olduğunu bildir (Upsert)"""
        # MAC adresi yoksa Ad üzerinden eşle
        result = self.execute_query("""
            INSERT INTO siramatik.cihazlar (firma_id, ad, tip, mac_adresi, aktif, son_gorunme, metadata)
            VALUES (:firma_id, :ad, :tip, :mac, TRUE, NOW(), :metadata::jsonb)
            ON CONFLICT (firma_id, mac_adresi) DO UPDATE 
            SET aktif = TRUE, son_gorunme = NOW(), tip = :tip, metadata = :metadata::jsonb
            RETURNING *
        """, {"firma_id": firma_id, "ad": ad, "tip": tip, "mac": mac or ad, "metadata": json.dumps(metadata)})
        return result[0] if result else None

    # --- İSTATİSTİKLER ---

    def get_firma_istatistikleri(self, firma_id: int, servis_id: Optional[int] = None, 
                                 kullanici_id: Optional[int] = None,
                                 period_type: str = "hour", time_range: str = "today",
                                 start_date: str = None, end_date: str = None) -> Dict:
        """Firma istatistiklerini getir (Gelişmiş Zaman ve Periyot Filtreli)"""
        params = {"firma_id": firma_id}
        
        # 1. ZAMAN FİLTRESİ OLUŞTUR
        time_filter = ""
        if time_range == "today":
            time_filter = " AND (s.olusturulma AT TIME ZONE 'Europe/Istanbul')::date = (NOW() AT TIME ZONE 'Europe/Istanbul')::date"
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

        # 3. KULLANICI FİLTRESİ
        user_filter = ""
        if kullanici_id:
            user_filter = " AND s.cagiran_kullanici_id = :kullanici_id"
            params["kullanici_id"] = kullanici_id

        # 4. TEMEL SAYILAR (Kartlar için)
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
            WHERE s.firma_id = :firma_id {time_filter} {service_filter} {user_filter}
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
            WHERE s.firma_id = :firma_id {time_filter} {service_filter} {user_filter}
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
            LEFT JOIN siramatik.siralar s ON ser.id = s.servis_id {time_filter} {user_filter}
            WHERE ser.firma_id = :firma_id {" AND ser.id = :servis_id" if servis_id else ""}
            GROUP BY ser.ad
        """, params)

        # 6. SON BİLETLER
        recent_tickets = self.execute_query(f"""
            SELECT s.id, s.numara, s.durum, to_char(s.olusturulma, 'DD.MM HH24:MI') as saat, ser.ad as servis_ad
            FROM siramatik.siralar s
            JOIN siramatik.servisler ser ON s.servis_id = ser.id
            WHERE s.firma_id = :firma_id {time_filter} {service_filter} {user_filter}
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

    def get_detailed_reports(self, firma_id: int, 
                             report_type: str = "transaction_log",
                             servis_id: Optional[int] = None,
                             kuyruk_id: Optional[int] = None,
                             kullanici_id: Optional[int] = None,
                             group_by: Optional[str] = None,
                             time_range: str = "today",
                             start_date: str = None, 
                             end_date: str = None) -> Dict:
        """Sektör Standartlarında BI Raporlama Motoru"""
        params = {"firma_id": firma_id}
        
        # 1. ZAMAN FİLTRESİ (Dinamik)
        time_filter = ""
        if time_range == "today":
            time_filter = " AND (s.olusturulma AT TIME ZONE 'Europe/Istanbul')::date = (NOW() AT TIME ZONE 'Europe/Istanbul')::date"
        elif time_range == "this_week":
            time_filter = " AND s.olusturulma >= date_trunc('week', CURRENT_DATE)"
        elif time_range == "this_month":
            time_filter = " AND s.olusturulma >= date_trunc('month', CURRENT_DATE)"
        elif time_range == "custom" and start_date:
            time_filter = " AND s.olusturulma::date BETWEEN :start AND :end"
            params["start"] = start_date
            params["end"] = end_date or start_date

        # 2. ESAS FİLTRELER
        extra_filters = ""
        if servis_id:
            extra_filters += " AND s.servis_id = :servis_id"
            params["servis_id"] = servis_id
        if kuyruk_id:
            extra_filters += " AND s.kuyruk_id = :kuyruk_id"
            params["kuyruk_id"] = kuyruk_id
        if kullanici_id:
            extra_filters += " AND s.cagiran_kullanici_id = :kullanici_id"
            params["kullanici_id"] = kullanici_id

        summary_query = f"""
            SELECT 
                COUNT(*) as toplam_bilet,
                COUNT(*) FILTER (WHERE durum = 'completed') as tamamlanan,
                AVG(CASE WHEN durum = 'completed' THEN EXTRACT(EPOCH FROM (cagirilma - olusturulma))/60 END) as ort_bekleme,
                AVG(CASE WHEN durum = 'completed' THEN EXTRACT(EPOCH FROM (tamamlanma - cagirilma))/60 END) as ort_islem
            FROM siramatik.siralar s
            WHERE s.firma_id = :firma_id {time_filter} {extra_filters}
        """
        summary = self.execute_query(summary_query, params)[0]

        # 3. GRUPLAMA MANTIĞI (Eğer seçilmişse ana raporu ezer)
        if group_by:
            group_col = ""
            group_label = ""
            join_clause = ""
            
            if group_by == "personel":
                group_col = "COALESCE(u.ad_soyad, 'Atanmamış')"
                group_label = "Personel"
                join_clause = "LEFT JOIN siramatik.kullanicilar u ON s.cagiran_kullanici_id = u.id"
            elif group_by == "servis":
                group_col = "ser.ad"
                group_label = "Bölüm"
                join_clause = "LEFT JOIN siramatik.servisler ser ON s.servis_id = ser.id"
            elif group_by == "kuyruk":
                group_col = "k.ad"
                group_label = "Kuyruk"
                join_clause = "LEFT JOIN siramatik.kuyruklar k ON s.kuyruk_id = k.id"
            elif group_by == "tarih":
                group_col = "(s.olusturulma AT TIME ZONE 'Europe/Istanbul')::date"
                group_label = "Tarih"

            if group_col:
                data = self.execute_query(f"""
                    SELECT {group_col}::text as grup, 
                           COUNT(*) as adet,
                           COUNT(*) FILTER (WHERE s.durum = 'completed') as tamamlanan,
                           ROUND(CAST(AVG(EXTRACT(EPOCH FROM (s.cagirilma - s.olusturulma))/60) AS NUMERIC), 1) as ort_bekleme,
                           ROUND(CAST(AVG(EXTRACT(EPOCH FROM (s.tamamlanma - s.cagirilma))/60) AS NUMERIC), 1) as ort_islem
                    FROM siramatik.siralar s
                    {join_clause}
                    WHERE s.firma_id = :firma_id {time_filter} {extra_filters}
                    GROUP BY grup ORDER BY adet DESC
                """, params)
                return {
                    "summary": summary,
                    "data": data,
                    "type": "grouped",
                    "group_label": group_label
                }

        # 4. RAPOR TİPİNE GÖRE SORGULAMA
        if report_type == "transaction_log":
            data = self.execute_query(f"""
                SELECT s.numara, ser.ad as servis, k.ad as kuyruk, u.ad_soyad as personel, 
                       to_char(s.olusturulma, 'DD.MM.YYYY') as tarih,
                       to_char(s.olusturulma, 'HH24:MI') as saat, s.durum,
                       ROUND(CAST(EXTRACT(EPOCH FROM (s.cagirilma - s.olusturulma))/60 AS NUMERIC), 1) as bekleme,
                       ROUND(CAST(EXTRACT(EPOCH FROM (s.tamamlanma - s.cagirilma))/60 AS NUMERIC), 1) as islem
                FROM siramatik.siralar s
                LEFT JOIN siramatik.servisler ser ON s.servis_id = ser.id
                LEFT JOIN siramatik.kuyruklar k ON s.kuyruk_id = k.id
                LEFT JOIN siramatik.kullanicilar u ON s.cagiran_kullanici_id = u.id
                WHERE s.firma_id = :firma_id {time_filter} {extra_filters}
                ORDER BY s.olusturulma DESC
            """, params)

        elif report_type == "staff_performance":
            data = self.execute_query(f"""
                SELECT u.ad_soyad as personel, 
                       COUNT(*) as toplam_islem,
                       ROUND(CAST(AVG(EXTRACT(EPOCH FROM (s.tamamlanma - s.cagirilma))/60) AS NUMERIC), 1) as ort_islem,
                       MAX(ROUND(CAST(EXTRACT(EPOCH FROM (s.tamamlanma - s.cagirilma))/60 AS NUMERIC), 1)) as max_islem,
                       COUNT(*) FILTER (WHERE durum = 'cancelled') as iptal_sayisi
                FROM siramatik.siralar s
                JOIN siramatik.kullanicilar u ON s.cagiran_kullanici_id = u.id
                WHERE s.firma_id = :firma_id {time_filter} {extra_filters}
                GROUP BY u.ad_soyad ORDER BY toplam_islem DESC
            """, params)

        elif report_type == "service_summary":
            data = self.execute_query(f"""
                SELECT ser.ad as servis, 
                       COUNT(*) as toplam_bilet,
                       COUNT(*) FILTER (WHERE durum = 'completed') as tamamlanan,
                       ROUND(CAST(AVG(EXTRACT(EPOCH FROM (s.cagirilma - s.olusturulma))/60) AS NUMERIC), 1) as ort_bekleme,
                       COUNT(*) FILTER (WHERE EXTRACT(EPOCH FROM (s.cagirilma - s.olusturulma))/60 > 15) as geciken_bilet
                FROM siramatik.siralar s
                JOIN siramatik.servisler ser ON s.servis_id = ser.id
                WHERE s.firma_id = :firma_id {time_filter} {extra_filters}
                GROUP BY ser.ad ORDER BY toplam_bilet DESC
            """, params)

        elif report_type == "hourly_density":
            data = self.execute_query(f"""
                SELECT to_char(s.olusturulma, 'HH24:00') as saat_araligi, 
                       COUNT(*) as bilet_sayisi,
                       COUNT(*) FILTER (WHERE durum = 'completed') as hizmet_verilen,
                       ROUND(CAST(AVG(EXTRACT(EPOCH FROM (s.cagirilma - s.olusturulma))/60) AS NUMERIC), 1) as ort_bekleme
                FROM siramatik.siralar s
                WHERE s.firma_id = :firma_id {time_filter} {extra_filters}
                GROUP BY saat_araligi ORDER BY saat_araligi
            """, params)

        elif report_type == "waiting_seg":
            data = self.execute_query(f"""
                SELECT CASE 
                         WHEN EXTRACT(EPOCH FROM (cagirilma - olusturulma))/60 < 5 THEN '0-5 dk (Hızlı)'
                         WHEN EXTRACT(EPOCH FROM (cagirilma - olusturulma))/60 < 15 THEN '5-15 dk (Normal)'
                         WHEN EXTRACT(EPOCH FROM (cagirilma - olusturulma))/60 < 30 THEN '15-30 dk (Yoğun)'
                         ELSE '30+ dk (Kritik)'
                       END as bekleme_grubu,
                       COUNT(*) as bilet_sayisi,
                       ROUND(CAST(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() AS NUMERIC), 1) as yuzde
                FROM siramatik.siralar s
                WHERE s.firma_id = :firma_id AND s.durum = 'completed' {time_filter} {extra_filters}
                GROUP BY bekleme_grubu
            """, params)

        elif report_type == "abandonment":
            data = self.execute_query(f"""
                SELECT ser.ad as servis, 
                       COUNT(*) as toplam_bilet,
                       COUNT(*) FILTER (WHERE durum = 'cancelled') as iptal,
                       COUNT(*) FILTER (WHERE durum = 'calling' AND cagirilma < NOW() - INTERVAL '5 minutes') as cevapsiz,
                       ROUND(CAST(COUNT(*) FILTER (WHERE durum = 'cancelled' OR durum = 'calling') * 100.0 / COUNT(*) AS NUMERIC), 1) as kayip_orani
                FROM siramatik.siralar s
                JOIN siramatik.servisler ser ON s.servis_id = ser.id
                WHERE s.firma_id = :firma_id {time_filter} {extra_filters}
                GROUP BY ser.ad
            """, params)

        elif report_type == "bonus_calc":
            data = self.execute_query(f"""
                SELECT u.ad_soyad as personel, 
                       COUNT(*) FILTER (WHERE durum = 'completed') as islem_sayisi,
                       ROUND(CAST(AVG(EXTRACT(EPOCH FROM (s.tamamlanma - s.cagirilma))/60) AS NUMERIC), 1) as ort_islem_suresi,
                       ROUND(CAST(
                           (COUNT(*) FILTER (WHERE durum = 'completed') * 10) - 
                           (AVG(EXTRACT(EPOCH FROM (s.tamamlanma - s.cagirilma))/60) * 2)
                       AS NUMERIC), 0) as performans_puani
                FROM siramatik.siralar s
                JOIN siramatik.kullanicilar u ON s.cagiran_kullanici_id = u.id
                WHERE s.firma_id = :firma_id {time_filter} {extra_filters}
                GROUP BY u.ad_soyad ORDER BY performans_puani DESC
            """, params)

        return {
            "summary": summary,
            "data": data,
            "type": report_type
        }


    # --- CIHAZ YONETIMI ---

    def cihaz_bildir(self, firma_id: int, ad: str, tip: str, mac: Optional[str], metadata: dict) -> Dict:
        """Cihaz kalp atışı - Kayıt yoksa oluştur, varsa güncelle"""
        
        # MAC adresi ile veya AD ile kontrol et (Varsa güncelle)
        existing = None
        
        if mac:
            existing_list = self.execute_query(
                "SELECT * FROM siramatik.cihazlar WHERE mac = :mac AND firma_id = :firma_id",
                {"mac": mac, "firma_id": firma_id}
            )
            if existing_list: existing = existing_list[0]
        elif ad:
             existing_list = self.execute_query(
                "SELECT * FROM siramatik.cihazlar WHERE ad = :ad AND firma_id = :firma_id",
                {"ad": ad, "firma_id": firma_id}
            )
             if existing_list: existing = existing_list[0]

        if existing:
            updated = self.execute_query("""
                UPDATE siramatik.cihazlar 
                SET son_gorulme = NOW(), metadata = :metadata, ad = :ad, tip = :tip
                WHERE id = :id
                RETURNING *
            """, {
                "id": existing["id"],
                "metadata": json.dumps(metadata),
                "ad": ad,
                "tip": tip
            })
            return updated[0]

        # Yeni kayıt oluştur
        result = self.execute_query("""
            INSERT INTO siramatik.cihazlar (firma_id, ad, tip, mac, metadata, son_gorulme)
            VALUES (:firma_id, :ad, :tip, :mac, :metadata, NOW())
            RETURNING *
        """, {
            "firma_id": firma_id,
            "ad": ad,
            "tip": tip,
            "mac": mac,
            "metadata": json.dumps(metadata)
        })
        return result[0]

    def get_cihazlar(self, firma_id: int) -> List[Dict]:
        """Firma cihazlarını listele"""
        return self.execute_query("""
            SELECT c.*, k.ad as konum_adi 
            FROM siramatik.cihazlar c
            LEFT JOIN siramatik.kuyruk_konumlar k ON c.konum = k.id
            WHERE c.firma_id = :firma_id 
            ORDER BY c.son_gorulme DESC
        """, {"firma_id": firma_id})

    def update_cihaz(self, cihaz_id: int, data: Dict) -> Dict:
        """Cihaz güncelle"""
        fields = []
        params = {"id": cihaz_id}
        
        for key, value in data.items():
            if key in ['ad', 'tip', 'konum_id', 'aktif']:
                fields.append(f"{key} = :{key}")
                params[key] = value
                
        if not fields:
            return None
            
        return self.execute_query(f"""
            UPDATE siramatik.cihazlar 
            SET {', '.join(fields)} 
            WHERE id = :id 
            RETURNING *
        """, params)[0]
        ticket = self.execute_query("SELECT * FROM siramatik.siralar WHERE id = :id", {"id": sira_id})
        if not ticket:
            return None
        
        ticket = ticket[0]
        
        # 2. Önündeki kişi sayısını hesapla
        # Aynı kuyrukta, waiting durumunda, önceliği daha yüksek olanlar
        # Veya önceliği aynı olup daha önce oluşturulanlar
        count = 0
        if ticket["durum"] == "waiting":
            res = self.execute_query("""
                SELECT COUNT(*) as count
                FROM siramatik.siralar
                WHERE kuyruk_id = :kuyruk_id
                  AND durum = 'waiting'
                  AND (
                      oncelik > :oncelik
                      OR (oncelik = :oncelik AND olusturulma < :olusturulma)
                  )
            """, {
                "kuyruk_id": ticket["kuyruk_id"],
                "oncelik": ticket["oncelik"],
                "olusturulma": ticket["olusturulma"]
            })
            count = res[0]["count"]
            
        return {
            "sira_id": ticket["id"],
            "numara": ticket["numara"],
            "durum": ticket["durum"],
            "bekleyen_sayisi": count
        }

# Global database instance
db = Database()
