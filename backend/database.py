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
import re
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# PostgreSQL Bağlantı URL'i (Supabase)
# Not: production ortamında connection pooling kullanılmalı
DB_URL = "postgresql://postgres.wyursjdrnnjabpfeucyi:qk4SEnyhu3NUk2@aws-1-eu-central-1.pooler.supabase.com:6543/postgres"

# Engine oluştur - search_path ile siramatik schema'yı belirt
# Engine oluştur - search_path ile siramatik schema'yı belirt
connect_args = {
    "options": "-c search_path=siramatik,public -c timezone=Europe/Istanbul",
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
            # Memnuniyet anketi tablosunu oluştur
            self._create_memnuniyet_table(session)
            # Tablet/Cihaz yönetim tablosunu oluştur
            self._create_cihazlar_table(session)
     
            # Cihaz tipleri ve kullanım tipleri referans tablosunu oluştur
            self._create_cihaz_tipleri_table(session)
            # Eski tip kolonu varsa bir kez cihaz_tipi/kullanim_tipi doldur, sonra tip kolonunu kaldır
            self._backfill_device_types(session)
            self._drop_cihazlar_tip_column(session)
            # Sistem ayarları tablosunu oluştur
            self._create_sistem_ayarlari_table(session)
            # Rapor şablonları tablosunu oluştur
            self._create_rapor_sablonlari_table(session)
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
            """))
            session.commit()

            # 2. Kolon Güncellemeleri (Toplu Try-Except bloğu yerine tek tek ama aynı bağlantıda)
            alter_queries = [
                "ALTER TABLE siramatik.firmalar ADD COLUMN IF NOT EXISTS sifre_kilitli BOOLEAN DEFAULT FALSE",
                "ALTER TABLE siramatik.firmalar ADD COLUMN IF NOT EXISTS sozlesme_bitis TIMESTAMP DEFAULT (NOW() + INTERVAL '1 year')",
                "ALTER TABLE siramatik.firmalar ADD COLUMN IF NOT EXISTS lisans_tipi VARCHAR(20) DEFAULT 'Kiralama'",
                "ALTER TABLE siramatik.firmalar ADD COLUMN IF NOT EXISTS max_cihaz INTEGER DEFAULT 10",
                "ALTER TABLE siramatik.firmalar ADD COLUMN IF NOT EXISTS notlar TEXT",
                "ALTER TABLE siramatik.firmalar ADD COLUMN IF NOT EXISTS erteleme BOOLEAN DEFAULT FALSE",
                "ALTER TABLE siramatik.firmalar ADD COLUMN IF NOT EXISTS erteleme_sayisi INTEGER DEFAULT 0",
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
                "ALTER TABLE siramatik.siralar ADD COLUMN IF NOT EXISTS notlar TEXT",
                "ALTER TABLE siramatik.siralar ADD COLUMN IF NOT EXISTS erteleme_sayisi INTEGER DEFAULT 0",
                "ALTER TABLE siramatik.siralar ADD COLUMN IF NOT EXISTS etkin_olusturulma TIMESTAMP"
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
            # Eski kayıtlar için etkin_olusturulma = olusturulma (tek seferlik backfill)
            try:
                session.execute(text("UPDATE siramatik.siralar SET etkin_olusturulma = olusturulma WHERE etkin_olusturulma IS NULL"))
                session.commit()
            except Exception:
                session.rollback()

    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        SQL sorgusu çalıştır.
        """
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
    
    # --- SİSTEM AYARLARI VE TIMEZONE YÖNETİMİ ---
    
    def _create_sistem_ayarlari_table(self, session):
        """Sistem ayarları tablosunu oluştur"""
        try:
            check_query = text("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_schema = 'siramatik' 
                    AND table_name = 'sistem_ayarlari'
                );
            """)
            result = session.execute(check_query).scalar()
            
            if result:
                print("[OK] sistem_ayarlari tablosu zaten var")
                return
            
            # Yeni tabloyu oluştur
            create_table_query = text("""
                CREATE TABLE IF NOT EXISTS siramatik.sistem_ayarlari (
                    id SERIAL PRIMARY KEY,
                    anahtar VARCHAR(100) UNIQUE NOT NULL,
                    deger TEXT NOT NULL,
                    aciklama TEXT,
                    olusturulma TIMESTAMP DEFAULT NOW(),
                    guncelleme TIMESTAMP DEFAULT NOW()
                );
                
                CREATE INDEX IF NOT EXISTS idx_sistem_ayarlari_anahtar ON siramatik.sistem_ayarlari(anahtar);
                
                COMMENT ON TABLE siramatik.sistem_ayarlari IS 'Sistem genel ayarları';
            """)
            
            session.execute(create_table_query)
            session.commit()
            print("[OK] sistem_ayarlari tablosu olusturuldu!")
            
        except Exception as e:
            print(f"[WARN] Sistem ayarları tablosu olusturma hatasi: {e}")
            session.rollback()
    
    def get_local_now(self) -> str:
        """
        Veritabanına yazılacak 'şu an' zamanı (SQL ifadesi).
        Direkt NOW() döndürür - Supabase database timezone'u zaten doğru ayarlı.
        """
        return "NOW()"

    def _local_date_sql(self, column_expr: str = "s.olusturulma") -> str:
        """
        Verdiğiniz sütunun tarihini döndüren SQL ifadesi.
        Direkt tarih olarak alınır - Supabase database timezone'u zaten doğru ayarlı.
        """
        return f"{column_expr}::date"

    def _today_local_sql(self) -> str:
        """
        'Bugün' tarihini döndüren SQL ifadesi.
        Direkt NOW() kullan - Supabase database timezone'u zaten doğru ayarlı.
        """
        return "NOW()::date"

    def _today_filter_sql(self, column_expr: str = "s.olusturulma") -> str:
        """Bugün (yerel) filtresi: column yerel tarihi = bugün yerel."""
        return f" AND {self._local_date_sql(column_expr)} = {self._today_local_sql()}"
    
    def _local_now_minus_interval(self, interval: str) -> str:
        """
        Şu anından belirtilen interval kadar öncesini döndürür.
        Örnek: interval='20 minutes' → (NOW() - INTERVAL '20 minutes')
        """
        return f"(NOW() - INTERVAL '{interval}')"
    
    def _local_now_plus_interval(self, interval: str) -> str:
        """
        Şu anından belirtilen interval kadar sonrasını döndürür.
        Örnek: interval='1 hour' → (NOW() + INTERVAL '1 hour')
        """
        return f"(NOW() + INTERVAL '{interval}')"
    
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

    def get_firma_erteleme_ayarlari(self, firma_id: int) -> Optional[Dict]:
        """Firmanın erteleme ayarlarını getir (bilet ekranı için public)."""
        result = self.execute_query(
            "SELECT erteleme, erteleme_sayisi FROM siramatik.firmalar WHERE id = :firma_id AND aktif = true",
            {"firma_id": firma_id}
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
        today_local = self._today_local_sql()
        col_local = self._local_date_sql("s.olusturulma")
        queues = self.execute_query(f"""
            SELECT k.*, 
                   (SELECT COUNT(*) FROM siramatik.siralar s 
                    WHERE s.kuyruk_id = k.id AND s.durum = 'waiting' 
                    AND {col_local} = {today_local}
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
        local_now = self.get_local_now()
        result = self.execute_query(f"""
            INSERT INTO siramatik.siralar (kuyruk_id, servis_id, firma_id, oncelik, notlar, numara, olusturulma, etkin_olusturulma)
            VALUES (:kuyruk_id, :servis_id, :firma_id, :oncelik, :notlar, 
                    siramatik.yeni_sira_numarasi(:kuyruk_id, :oncelik), {local_now}, {local_now})
            RETURNING *
        """, {
            "kuyruk_id": kuyruk_id,
            "servis_id": servis_id,
            "firma_id": firma_id,
            "oncelik": oncelik,
            "notlar": notlar
        })
        return result[0] if result else None
    
    def get_next_manuel_numara(self, firma_id: int, prefix: str = "X") -> str:
        """Bugün için verilen ön ek (X, K vb.) ile bir sonraki numarayı döndürür. Her gün 001'den başlar."""
        if not prefix or not prefix.strip():
            prefix = "X"
        prefix = str(prefix).strip().upper()[:1]  # Tek harf
        today_filter = self._today_filter_sql("olusturulma")  # Tablo alias yok, direkt sütun adı
        # Bugün aynı firma ve aynı ön ekle başlayan numaralardan en büyük sayıyı bul
        rows = self.execute_query(f"""
            SELECT numara FROM siramatik.siralar
            WHERE firma_id = :firma_id AND numara LIKE :prefix_pattern {today_filter}
        """, {"firma_id": firma_id, "prefix_pattern": prefix + "%"})
        next_num = 1
        if rows:
            for r in rows:
                numara = (r.get("numara") or "")
                # Ön eki çıkar, kalanı sayıya çevir (X001 -> 1, X002 -> 2)
                suffix = re.sub(r"^[A-Za-z]+", "", numara)
                if suffix.isdigit():
                    next_num = max(next_num, int(suffix) + 1)
        return f"{prefix}{next_num:03d}"

    def create_manuel_sira(self, kuyruk_id: int, servis_id: int, firma_id: int, 
                           numara: Optional[str], oncelik: int = 0, notlar: str = None) -> Dict:
        """Manuel sıra oluştur. numara boş veya sadece seri harfi (X) ise bugün için otomatik artan numara atanır (X001, X002, ...)."""
        local_now = self.get_local_now()
        prefix = (numara or "X").strip().upper()
        # Boş, sadece harf veya sadece seri ise otomatik numara üret
        if not numara or not numara.strip() or (len(prefix) <= 1 and prefix.isalpha()):
            numara = self.get_next_manuel_numara(firma_id, prefix if prefix else "X")
        result = self.execute_query(f"""
            INSERT INTO siramatik.siralar (kuyruk_id, servis_id, firma_id, oncelik, notlar, numara, olusturulma, etkin_olusturulma)
            VALUES (:kuyruk_id, :servis_id, :firma_id, :oncelik, :notlar, :numara, {local_now}, {local_now})
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
        """Belirli bir kuyruktaki TÜM bekleyen sıraları getir.

        Burada **hiçbir tarih filtresi yok**. Bunun sebebi:
        - Ekranlarda gördüğümüz hata, gün/tarih hesaplarındaki offset farkından kaynaklanıyordu.
        - Çağrı mantığı açısından önemli olan; aynı kuyruktaki, durumu 'waiting' olan
          kayıtların **öncelik** ve **olusturulma** zamanına göre sıralanması.
        - Zaten eski kayıtlar periyodik temizleme fonksiyonlarıyla siliniyor.

        Sıralama: önce yüksek öncelik, sonra en eski etkin_olusturulma (erteleme sonrası sıra konumu).
        """
        return self.execute_query("""
            SELECT * FROM siramatik.siralar
            WHERE kuyruk_id = :kuyruk_id
              AND durum = 'waiting'
            ORDER BY oncelik DESC, COALESCE(etkin_olusturulma, olusturulma) ASC
        """, {"kuyruk_id": kuyruk_id})
    
    def cagir_sira(self, sira_id: int, kullanici_id: int, konum: str = None) -> Dict:
        """Sırayı çağır"""
        local_now = self.get_local_now()
        result = self.execute_query(f"""
            UPDATE siramatik.siralar 
            SET durum = 'calling', 
                cagiran_kullanici_id = :kullanici_id,
                konum = :konum,
                cagirilma = {local_now}
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
        local_now = self.get_local_now()
        result = self.execute_query(f"""
            UPDATE siramatik.siralar 
            SET durum = 'completed', tamamlanma = {local_now}
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
        local_now = self.get_local_now()
        result = self.execute_query(f"""
            UPDATE siramatik.siralar 
            SET durum = 'serving', islem_baslangic = {local_now}
            WHERE id = :sira_id
            RETURNING *
        """, {"sira_id": sira_id})
        return result[0] if result else None

    def tekrar_cagir(self, sira_id: int) -> Dict:
        """Sırayı tekrar çağır (TV'de flaşlat)"""
        local_now = self.get_local_now()
        result = self.execute_query(f"""
            UPDATE siramatik.siralar 
            SET cagirilma = {local_now}, cagirilma_sayisi = cagirilma_sayisi + 1
            WHERE id = :sira_id
            RETURNING *
        """, {"sira_id": sira_id})
        return result[0] if result else None

    def gelmedi_sira(self, sira_id: int) -> Dict:
        """Sırayı gelmedi olarak işaretle"""
        local_now = self.get_local_now()
        result = self.execute_query(f"""
            UPDATE siramatik.siralar 
            SET durum = 'skipped', tamamlanma = {local_now}
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
        """Ekran için son çağrıları getir (yerel gün filtresi)"""
        today_filter = self._today_filter_sql("s.olusturulma")
        query = f"""
            SELECT 
                s.*, 
                ser.ad as servis_ad,
                k.ad as kuyruk_ad
            FROM siramatik.siralar s
            LEFT JOIN siramatik.servisler ser ON s.servis_id = ser.id
            LEFT JOIN siramatik.kuyruklar k ON s.kuyruk_id = k.id
            WHERE s.firma_id = :firma_id 
            AND s.durum = 'calling'
            {today_filter}
            AND s.cagirilma > {self._local_now_minus_interval("20 minutes")}
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
        """Firmaya ait bugün oluşturulmuş bekleyen sıraları getir (gece yarısından sonra oluşturulanlar)."""
        today_filter = self._today_filter_sql("s.olusturulma")
        return self.execute_query(f"""
            SELECT s.* 
            FROM siramatik.siralar s
            JOIN siramatik.kuyruklar k ON s.kuyruk_id = k.id
            JOIN siramatik.servisler sv ON k.servis_id = sv.id
            WHERE sv.firma_id = :firma_id 
            AND s.durum = 'waiting'
            {today_filter}
            ORDER BY COALESCE(s.oncelik, 0) DESC, COALESCE(s.etkin_olusturulma, s.olusturulma) ASC
        """, {"firma_id": firma_id})

    def discard_bekleyen_siralar(self, firma_id: int) -> int:
        """Mesai bitimi: firmadaki tüm bekleyen biletleri 'discarded' yap. İstatistikleri bozmaz (completed sayılmaz)."""
        local_now = self._local_now_sql()
        r = self.execute_query("""
            UPDATE siramatik.siralar
            SET durum = 'discarded', tamamlanma = """ + local_now + """
            WHERE firma_id = :firma_id AND durum = 'waiting'
            RETURNING id
        """, {"firma_id": firma_id})
        return len(r) if r else 0
        
    def get_gunluk_istatistik(self, firma_id: str, kullanici_id: Optional[str] = None) -> Dict:
        """Günlük istatistikleri getir"""
        
        # Personel bazlı toplam (Eğer kullanici_id varsa)
        parametreler = {"firma_id": firma_id}
        
        today_filter = self._today_filter_sql("s.olusturulma")
        sql_toplam = f"""
            SELECT COUNT(*) as sayi 
            FROM siramatik.siralar s
            JOIN siramatik.kuyruklar k ON s.kuyruk_id = k.id
            JOIN siramatik.servisler sv ON k.servis_id = sv.id
            WHERE sv.firma_id = :firma_id 
            {today_filter}
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
        """, {"firma_id": firma_id})
        
        # Ortalama İşlem Süresi (Bugün yerel, Tamamlananlar)
        sql_avg = f"""
            SELECT AVG(EXTRACT(EPOCH FROM (tamamlanma - COALESCE(islem_baslangic, cagirilma)))) / 60 as ort_dk
            FROM siramatik.siralar s
            JOIN siramatik.kuyruklar k ON s.kuyruk_id = k.id
            JOIN siramatik.servisler sv ON k.servis_id = sv.id
            WHERE sv.firma_id = :firma_id 
            AND s.durum = 'completed'
            AND s.tamamlanma IS NOT NULL
            {today_filter}
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
            ORDER BY c.kullanim_tipi, c.ad
        """, {"firma_id": firma_id})

    def get_cihaz(self, cihaz_id: int) -> Optional[Dict]:
        """Cihaz bilgisini getir (cihaz_tipi, kullanim_tipi dahil)"""
        result = self.execute_query("""
                SELECT 
                id, firma_id, ad, cihaz_tipi, kullanim_tipi, device_fingerprint, mac_address, ip,
                durum, son_gorulen, ayarlar, metadata, olusturulma, guncelleme,
                servis_id, kuyruk_id, setup_tamamlandi
            FROM siramatik.cihazlar 
            WHERE id = :cihaz_id
        """, {"cihaz_id": cihaz_id})
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
        """Cihazın aktif olduğunu bildir (Upsert). Eski endpoint; tip değeri cihaz_tipi/kullanim_tipi olarak türetilir."""
        local_now = self.get_local_now()
        leg = (tip or "").lower()
        cihaz_tipi = {"kiosk": "TABLET", "tablet": "TABLET", "ekran": "TV", "pc": "PC"}.get(leg)
        kullanim_tipi = {"kiosk": "KIOSK", "tablet": "KIOSK", "ekran": "EKRAN", "pc": "KULLANICI_EKRANI"}.get(leg)
        result = self.execute_query(f"""
            INSERT INTO siramatik.cihazlar (firma_id, ad, cihaz_tipi, kullanim_tipi, mac_address, durum, son_gorulen, metadata)
            VALUES (:firma_id, :ad, :cihaz_tipi, :kullanim_tipi, :mac, 'active', {local_now}, :metadata::jsonb)
            ON CONFLICT (device_fingerprint) DO UPDATE 
            SET durum = 'active', son_gorulen = {local_now}, cihaz_tipi = COALESCE(EXCLUDED.cihaz_tipi, cihazlar.cihaz_tipi), kullanim_tipi = COALESCE(EXCLUDED.kullanim_tipi, cihazlar.kullanim_tipi), metadata = EXCLUDED.metadata
            RETURNING *
        """, {"firma_id": firma_id, "ad": ad, "cihaz_tipi": cihaz_tipi, "kullanim_tipi": kullanim_tipi, "mac": mac or ad, "metadata": json.dumps(metadata)})
        return result[0] if result else None

    # --- İSTATİSTİKLER ---

    def get_firma_istatistikleri(self, firma_id: int, servis_id: Optional[int] = None, 
                                 kullanici_id: Optional[int] = None,
                                 period_type: str = "hour", time_range: str = "today",
                                 start_date: str = None, end_date: str = None) -> Dict:
        """Firma istatistiklerini getir (Gelişmiş Zaman ve Periyot Filtreli)"""
        params = {"firma_id": firma_id}
        
        # 1. ZAMAN FİLTRESİ OLUŞTUR (yerel tarih: timezone_offset)
        time_filter = ""
        if time_range == "today":
            time_filter = self._today_filter_sql("s.olusturulma")
        elif time_range == "this_week":
            time_filter = " AND s.olusturulma >= date_trunc('week', CURRENT_DATE)"
        elif time_range == "this_month":
            time_filter = " AND s.olusturulma >= date_trunc('month', CURRENT_DATE)"
        elif time_range == "last_month":
            time_filter = " AND s.olusturulma >= date_trunc('month', CURRENT_DATE - INTERVAL '1 month') AND s.olusturulma < date_trunc('month', CURRENT_DATE)"
        elif time_range == "this_year":
            time_filter = " AND s.olusturulma >= date_trunc('year', CURRENT_DATE)"
        elif time_range == "last_year":
            time_filter = " AND s.olusturulma >= date_trunc('year', CURRENT_DATE - INTERVAL '1 year') AND s.olusturulma < date_trunc('year', CURRENT_DATE)"
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
                AVG(CASE WHEN durum = 'completed' THEN EXTRACT(EPOCH FROM (cagirilma - COALESCE(etkin_olusturulma, olusturulma)))/60 END) as ort_bekleme_dk,
                AVG(CASE WHEN durum = 'completed' THEN EXTRACT(EPOCH FROM (tamamlanma - cagirilma))/60 END) as ort_islem_dk
            FROM siramatik.siralar s
            WHERE s.firma_id = :firma_id {time_filter} {service_filter} {user_filter}
        """, params)[0]

        # 4. PERİYOT GRUPLAMA (Grafik için)
        group_sql = ""
        label_format = ""
        etkin_col = "COALESCE(s.etkin_olusturulma, s.olusturulma)"
        if period_type == "hour":
            group_sql = f"EXTRACT(HOUR FROM {etkin_col})"
            label_format = "saat"
        elif period_type == "weekday":
            group_sql = f"EXTRACT(DOW FROM {etkin_col})"
            label_format = "gün" # 0: Pazar, 1: Pazartesi...
        elif period_type == "monthday":
            group_sql = f"EXTRACT(DAY FROM {etkin_col})"
            label_format = "gün"
        elif period_type == "week":
            group_sql = f"EXTRACT(WEEK FROM {etkin_col})"
            label_format = "hafta"
        elif period_type == "month":
            group_sql = f"EXTRACT(MONTH FROM {etkin_col})"
            label_format = "ay"
        else:
            group_sql = f"EXTRACT(HOUR FROM {etkin_col})"
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

        # 6. SON BİLETLER (etkin zamana göre sıra ve gösterim)
        recent_tickets = self.execute_query(f"""
            SELECT s.id, s.numara, s.durum, to_char(COALESCE(s.etkin_olusturulma, s.olusturulma), 'DD.MM HH24:MI') as saat, ser.ad as servis_ad
            FROM siramatik.siralar s
            JOIN siramatik.servisler ser ON s.servis_id = ser.id
            WHERE s.firma_id = :firma_id {time_filter} {service_filter} {user_filter}
            ORDER BY COALESCE(s.etkin_olusturulma, s.olusturulma) DESC LIMIT 10
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
        
        # 1. ZAMAN FİLTRESİ (yerel tarih: timezone_offset)
        time_filter = ""
        if time_range == "today":
            time_filter = self._today_filter_sql("s.olusturulma")
        elif time_range == "this_week":
            time_filter = " AND s.olusturulma >= date_trunc('week', CURRENT_DATE)"
        elif time_range == "this_month":
            time_filter = " AND s.olusturulma >= date_trunc('month', CURRENT_DATE)"
        elif time_range == "last_month":
            time_filter = " AND s.olusturulma >= date_trunc('month', CURRENT_DATE - INTERVAL '1 month') AND s.olusturulma < date_trunc('month', CURRENT_DATE)"
        elif time_range == "last_year":
            time_filter = " AND s.olusturulma >= date_trunc('year', CURRENT_DATE - INTERVAL '1 year') AND s.olusturulma < date_trunc('year', CURRENT_DATE)"
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
                AVG(CASE WHEN durum = 'completed' THEN EXTRACT(EPOCH FROM (cagirilma - COALESCE(etkin_olusturulma, olusturulma)))/60 END) as ort_bekleme,
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
                group_col = self._local_date_sql("COALESCE(s.etkin_olusturulma, s.olusturulma)")
                group_label = "Tarih"

            if group_col:
                data = self.execute_query(f"""
                    SELECT {group_col}::text as grup, 
                           COUNT(*) as adet,
                           COUNT(*) FILTER (WHERE s.durum = 'completed') as tamamlanan,
                           ROUND(CAST(AVG(EXTRACT(EPOCH FROM (s.cagirilma - COALESCE(s.etkin_olusturulma, s.olusturulma)))/60) AS NUMERIC), 1) as ort_bekleme,
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
            # CTE için zaman filtresi (s2 tablosunu kullanmalı)
            time_filter_cte = time_filter.replace(" AND s.", " AND s2.")
            
            data = self.execute_query(f"""
                WITH personel_istatistik AS (
                    SELECT 
                        s2.cagiran_kullanici_id,
                        COUNT(DISTINCT s2.id) as toplam_hasta,
                        COUNT(DISTINCT ma.id) as puanlama_yapan,
                        CASE 
                            WHEN COUNT(DISTINCT s2.id) > 0 
                            THEN ROUND(CAST(COUNT(DISTINCT ma.id) * 100.0 / COUNT(DISTINCT s2.id) AS NUMERIC), 1)
                            ELSE 0
                        END as puanlama_orani,
                        ROUND(CAST(AVG(ma.puan) AS NUMERIC), 2) as ortalama_puan
                    FROM siramatik.siralar s2
                    LEFT JOIN siramatik.memnuniyet_anketleri ma ON s2.id = ma.sira_id
                    WHERE s2.firma_id = :firma_id {time_filter_cte}
                    GROUP BY s2.cagiran_kullanici_id
                )
                SELECT s.numara, ser.ad as servis, k.ad as kuyruk, u.ad_soyad as personel, 
                       to_char(COALESCE(s.etkin_olusturulma, s.olusturulma), 'DD.MM.YYYY') as tarih,
                       to_char(COALESCE(s.etkin_olusturulma, s.olusturulma), 'HH24:MI') as saat, s.durum,
                       ROUND(CAST(EXTRACT(EPOCH FROM (s.cagirilma - COALESCE(s.etkin_olusturulma, s.olusturulma)))/60 AS NUMERIC), 1) as bekleme,
                       ROUND(CAST(EXTRACT(EPOCH FROM (s.tamamlanma - s.cagirilma))/60 AS NUMERIC), 1) as islem,
                       COALESCE(pi.puanlama_orani, 0) as puanlama_orani,
                       COALESCE(pi.ortalama_puan, 0) as ortalama_puan
                FROM siramatik.siralar s
                LEFT JOIN siramatik.servisler ser ON s.servis_id = ser.id
                LEFT JOIN siramatik.kuyruklar k ON s.kuyruk_id = k.id
                LEFT JOIN siramatik.kullanicilar u ON s.cagiran_kullanici_id = u.id
                LEFT JOIN personel_istatistik pi ON s.cagiran_kullanici_id = pi.cagiran_kullanici_id
                WHERE s.firma_id = :firma_id {time_filter} {extra_filters}
                ORDER BY COALESCE(s.etkin_olusturulma, s.olusturulma) DESC
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
                       ROUND(CAST(AVG(EXTRACT(EPOCH FROM (s.cagirilma - COALESCE(s.etkin_olusturulma, s.olusturulma)))/60) AS NUMERIC), 1) as ort_bekleme,
                       COUNT(*) FILTER (WHERE EXTRACT(EPOCH FROM (s.cagirilma - COALESCE(s.etkin_olusturulma, s.olusturulma)))/60 > 15) as geciken_bilet
                FROM siramatik.siralar s
                JOIN siramatik.servisler ser ON s.servis_id = ser.id
                WHERE s.firma_id = :firma_id {time_filter} {extra_filters}
                GROUP BY ser.ad ORDER BY toplam_bilet DESC
            """, params)

        elif report_type == "hourly_density":
            data = self.execute_query(f"""
                SELECT to_char(COALESCE(s.etkin_olusturulma, s.olusturulma), 'HH24:00') as saat_araligi, 
                       COUNT(*) as bilet_sayisi,
                       COUNT(*) FILTER (WHERE durum = 'completed') as hizmet_verilen,
                       ROUND(CAST(AVG(EXTRACT(EPOCH FROM (s.cagirilma - COALESCE(s.etkin_olusturulma, s.olusturulma)))/60) AS NUMERIC), 1) as ort_bekleme
                FROM siramatik.siralar s
                WHERE s.firma_id = :firma_id {time_filter} {extra_filters}
                GROUP BY saat_araligi ORDER BY saat_araligi
            """, params)

        elif report_type == "waiting_seg":
            data = self.execute_query(f"""
                SELECT CASE 
                         WHEN EXTRACT(EPOCH FROM (cagirilma - COALESCE(etkin_olusturulma, olusturulma)))/60 < 5 THEN '0-5 dk (Hızlı)'
                         WHEN EXTRACT(EPOCH FROM (cagirilma - COALESCE(etkin_olusturulma, olusturulma)))/60 < 15 THEN '5-15 dk (Normal)'
                         WHEN EXTRACT(EPOCH FROM (cagirilma - COALESCE(etkin_olusturulma, olusturulma)))/60 < 30 THEN '15-30 dk (Yoğun)'
                         ELSE '30+ dk (Kritik)'
                       END as bekleme_grubu,
                       COUNT(*) as bilet_sayisi,
                       ROUND(CAST(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() AS NUMERIC), 1) as yuzde
                FROM siramatik.siralar s
                WHERE s.firma_id = :firma_id AND s.durum = 'completed' {time_filter} {extra_filters}
                GROUP BY bekleme_grubu
            """, params)

        elif report_type == "abandonment":
            local_5min_ago = self._local_now_minus_interval("5 minutes")
            data = self.execute_query(f"""
                SELECT ser.ad as servis, 
                       COUNT(*) as toplam_bilet,
                       COUNT(*) FILTER (WHERE durum = 'cancelled') as iptal,
                       COUNT(*) FILTER (WHERE durum = 'calling' AND cagirilma < {local_5min_ago}) as cevapsiz,
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
        """Cihaz kalp atışı - Kayıt yoksa oluştur, varsa güncelle. tip değeri cihaz_tipi/kullanim_tipi olarak türetilir."""
        leg = (tip or "").lower()
        cihaz_tipi = {"kiosk": "TABLET", "tablet": "TABLET", "ekran": "TV", "pc": "PC"}.get(leg)
        kullanim_tipi = {"kiosk": "KIOSK", "tablet": "KIOSK", "ekran": "EKRAN", "pc": "KULLANICI_EKRANI"}.get(leg)
        existing = None
        local_now = self.get_local_now()
        if mac:
            existing_list = self.execute_query(
                "SELECT * FROM siramatik.cihazlar WHERE mac_address = :mac AND firma_id = :firma_id",
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
            updated = self.execute_query(f"""
                UPDATE siramatik.cihazlar 
                SET son_gorulen = {local_now}, metadata = :metadata, ad = :ad, cihaz_tipi = COALESCE(:cihaz_tipi, cihaz_tipi), kullanim_tipi = COALESCE(:kullanim_tipi, kullanim_tipi)
                WHERE id = :id
                RETURNING *
            """, {
                "id": existing["id"],
                "metadata": json.dumps(metadata),
                "ad": ad,
                "cihaz_tipi": cihaz_tipi,
                "kullanim_tipi": kullanim_tipi
            })
            return updated[0]

        result = self.execute_query(f"""
            INSERT INTO siramatik.cihazlar (firma_id, ad, cihaz_tipi, kullanim_tipi, mac_address, metadata, son_gorulen)
            VALUES (:firma_id, :ad, :cihaz_tipi, :kullanim_tipi, :mac_address, :metadata, {local_now})
            RETURNING *
        """, {
            "firma_id": firma_id,
            "ad": ad,
            "cihaz_tipi": cihaz_tipi,
            "kullanim_tipi": kullanim_tipi,
            "mac_address": mac,
            "metadata": json.dumps(metadata)
        })
        return result[0]

    def get_cihazlar(self, firma_id: int) -> List[Dict]:
        """Firma cihazlarını listele"""
        return self.execute_query("""
            SELECT c.*
            FROM siramatik.cihazlar c
            WHERE c.firma_id = :firma_id 
            ORDER BY c.son_gorulen DESC
        """, {"firma_id": firma_id})

    def update_cihaz(self, cihaz_id: int, data: Dict) -> Dict:
        """Cihaz güncelle"""
        local_now = self.get_local_now()
        fields = []
        params = {"id": cihaz_id}
        
        for key, value in data.items():
            if key in ['ad', 'konum_id', 'aktif', 'servis_id', 'kuyruk_id', 'durum', 'cihaz_tipi', 'kullanim_tipi']:
                fields.append(f"{key} = :{key}")
                params[key] = value
                
        if not fields:
            return None
        
        # guncelleme alanını da yerel saat ile güncelle
        fields.append(f"guncelleme = {local_now}")
            
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
        
        # 2. Önündeki kişi sayısını hesapla (sıra konumu = etkin_olusturulma)
        etkin = ticket.get("etkin_olusturulma") or ticket.get("olusturulma")
        count = 0
        if ticket["durum"] == "waiting":
            res = self.execute_query("""
                SELECT COUNT(*) as count
                FROM siramatik.siralar
                WHERE kuyruk_id = :kuyruk_id
                  AND durum = 'waiting'
                  AND (
                      oncelik > :oncelik
                      OR (oncelik = :oncelik AND COALESCE(etkin_olusturulma, olusturulma) < :etkin_olusturulma)
                  )
            """, {
                "kuyruk_id": ticket["kuyruk_id"],
                "oncelik": ticket["oncelik"],
                "etkin_olusturulma": etkin
            })
            count = res[0]["count"]
            
        return {
            "sira_id": ticket["id"],
            "numara": ticket["numara"],
            "durum": ticket["durum"],
            "bekleyen_sayisi": count
        }

    def ertele_sira(self, sira_id: int, dakika: int) -> Optional[Dict]:
        """
        Biletin sırasını X dakika geciktirir: etkin_olusturulma += dakika (olusturulma değişmez, ertelenen bilet belli olur).
        Koşullar: bilet waiting, firma erteleme açık, biletin erteleme hakkı kalmış.
        """
        if not isinstance(dakika, int) or dakika < 1 or dakika > 60:
            return None
        ticket = self.execute_query("SELECT id, kuyruk_id, firma_id, durum, COALESCE(erteleme_sayisi, 0) as erteleme_sayisi FROM siramatik.siralar WHERE id = :id", {"id": sira_id})
        if not ticket:
            return None
        ticket = ticket[0]
        if ticket["durum"] != "waiting":
            return None
        firma = self.get_firma_erteleme_ayarlari(ticket["firma_id"])
        if not firma or not firma.get("erteleme"):
            return None
        limit = int(firma.get("erteleme_sayisi") or 0)
        if limit <= 0:
            return None
        kullanilan = int(ticket.get("erteleme_sayisi") or 0)
        if kullanilan >= limit:
            return None
        result = self.execute_query("""
            UPDATE siramatik.siralar
            SET etkin_olusturulma = COALESCE(etkin_olusturulma, olusturulma) + (:dakika || ' minutes')::interval,
                erteleme_sayisi = COALESCE(erteleme_sayisi, 0) + 1
            WHERE id = :sira_id AND durum = 'waiting'
            RETURNING *
        """, {"sira_id": sira_id, "dakika": dakika})
        return result[0] if result else None
    
    def _create_memnuniyet_table(self, session):
        """Memnuniyet anketi tablosunu oluştur"""
        try:
            # Tablo var mı kontrol et
            check_query = text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'siramatik' 
                    AND table_name = 'memnuniyet_anketleri'
                );
            """)
            result = session.execute(check_query).scalar()
            
            if result:
                print("[OK] memnuniyet_anketleri tablosu zaten var")
                try:
                    session.execute(text("""
                        ALTER TABLE siramatik.memnuniyet_anketleri
                        DROP CONSTRAINT IF EXISTS memnuniyet_anketleri_puan_check;
                        ALTER TABLE siramatik.memnuniyet_anketleri
                        ADD CONSTRAINT memnuniyet_anketleri_puan_check CHECK (puan >= 0 AND puan <= 100);
                    """))
                    session.commit()
                    print("[OK] memnuniyet_anketleri puan kısıtı 0-100 olarak güncellendi")
                except Exception as alter_e:
                    session.rollback()
                    print(f"[WARN] Puan kısıtı güncellenemedi (zaten 0-100 olabilir): {alter_e}")
                return
            
            # Tabloyu oluştur (puan 0-100, 100 üzerinden değerlendirme)
            create_table_query = text("""
                CREATE TABLE IF NOT EXISTS siramatik.memnuniyet_anketleri (
                    id SERIAL PRIMARY KEY,
                    sira_id INTEGER NOT NULL,
                    kuyruk_id INTEGER NOT NULL,
                    servis_id INTEGER,
                    firma_id INTEGER NOT NULL,
                    cagiran_kullanici_id INTEGER,
                    puan INTEGER NOT NULL CHECK (puan >= 0 AND puan <= 100),
                    yorum TEXT,
                    anket_tarihi TIMESTAMPTZ DEFAULT NOW(),
                    ip_adresi VARCHAR(45),
                    cihaz_bilgisi TEXT,
                    hizmet_suresi_dk INTEGER
                );
                
                CREATE INDEX IF NOT EXISTS idx_memnuniyet_sira ON siramatik.memnuniyet_anketleri(sira_id);
                CREATE INDEX IF NOT EXISTS idx_memnuniyet_kuyruk ON siramatik.memnuniyet_anketleri(kuyruk_id);
                CREATE INDEX IF NOT EXISTS idx_memnuniyet_puan ON siramatik.memnuniyet_anketleri(puan);
                CREATE INDEX IF NOT EXISTS idx_memnuniyet_tarih ON siramatik.memnuniyet_anketleri(anket_tarihi);
                
                ALTER TABLE siramatik.memnuniyet_anketleri ENABLE ROW LEVEL SECURITY;
                
                DROP POLICY IF EXISTS memnuniyet_select_policy ON siramatik.memnuniyet_anketleri;
                CREATE POLICY memnuniyet_select_policy ON siramatik.memnuniyet_anketleri
                    FOR SELECT USING (true);
                
                DROP POLICY IF EXISTS memnuniyet_insert_policy ON siramatik.memnuniyet_anketleri;
                CREATE POLICY memnuniyet_insert_policy ON siramatik.memnuniyet_anketleri
                    FOR INSERT WITH CHECK (true);
                
                COMMENT ON TABLE siramatik.memnuniyet_anketleri IS 'Müşteri memnuniyet anketleri';
            """)
            
            session.execute(create_table_query)
            session.commit()
            print("[OK] memnuniyet_anketleri tablosu olusturuldu!")
            
        except Exception as e:
            print(f"[WARN] Memnuniyet tablosu olusturma hatasi: {e}")
            session.rollback()
    
    def _create_cihazlar_table(self, session):
        """Cihazlar (Tablet/Kiosk) tablosunu oluştur"""
        try:
            # Tablo var mı ve doğru kolonlar var mı kontrol et
            check_query = text("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_schema = 'siramatik' 
                    AND table_name = 'cihazlar'
                    AND column_name = 'device_fingerprint'
                );
            """)
            result = session.execute(check_query).scalar()
            
            if result:
                print("[OK] cihazlar tablosu (device_fingerprint ile) zaten var")
                # Tablo varsa bile kolonları kontrol et ve ekle
                try:
                    session.execute(text("""
                        DO $$ 
                        BEGIN
                            -- servis_id kolonu yoksa ekle
                            IF NOT EXISTS (
                                SELECT 1 FROM information_schema.columns 
                                WHERE table_schema = 'siramatik' 
                                AND table_name = 'cihazlar' 
                                AND column_name = 'servis_id'
                            ) THEN
                                ALTER TABLE siramatik.cihazlar 
                                ADD COLUMN servis_id INTEGER REFERENCES siramatik.servisler(id) ON DELETE SET NULL;
                                CREATE INDEX IF NOT EXISTS idx_cihazlar_servis_id ON siramatik.cihazlar(servis_id);
                            END IF;
                            
                            -- kuyruk_id kolonu yoksa ekle
                            IF NOT EXISTS (
                                SELECT 1 FROM information_schema.columns 
                                WHERE table_schema = 'siramatik' 
                                AND table_name = 'cihazlar' 
                                AND column_name = 'kuyruk_id'
                            ) THEN
                                ALTER TABLE siramatik.cihazlar 
                                ADD COLUMN kuyruk_id INTEGER REFERENCES siramatik.kuyruklar(id) ON DELETE SET NULL;
                                CREATE INDEX IF NOT EXISTS idx_cihazlar_kuyruk_id ON siramatik.cihazlar(kuyruk_id);
                            END IF;
                            
                            -- ip kolonu yoksa veya ip_address ise düzelt
                            IF EXISTS (
                                SELECT 1 FROM information_schema.columns 
                                WHERE table_schema = 'siramatik' 
                                AND table_name = 'cihazlar' 
                                AND column_name = 'ip_address'
                            ) AND NOT EXISTS (
                                SELECT 1 FROM information_schema.columns 
                                WHERE table_schema = 'siramatik' 
                                AND table_name = 'cihazlar' 
                                AND column_name = 'ip'
                            ) THEN
                                ALTER TABLE siramatik.cihazlar RENAME COLUMN ip_address TO ip;
                            END IF;
                            
                            -- ip kolonu yoksa ekle
                            IF NOT EXISTS (
                                SELECT 1 FROM information_schema.columns 
                                WHERE table_schema = 'siramatik' 
                                AND table_name = 'cihazlar' 
                                AND column_name = 'ip'
                            ) THEN
                                ALTER TABLE siramatik.cihazlar 
                                ADD COLUMN ip VARCHAR(50);
                            END IF;

                            -- setup_tamamlandi kolonu yoksa ekle
                            IF NOT EXISTS (
                                SELECT 1 FROM information_schema.columns 
                                WHERE table_schema = 'siramatik' 
                                AND table_name = 'cihazlar' 
                                AND column_name = 'setup_tamamlandi'
                            ) THEN
                                ALTER TABLE siramatik.cihazlar 
                                ADD COLUMN setup_tamamlandi BOOLEAN NOT NULL DEFAULT FALSE;
                            END IF;

                            -- cihaz_tipi kolonu yoksa ekle
                            IF NOT EXISTS (
                                SELECT 1 FROM information_schema.columns 
                                WHERE table_schema = 'siramatik' 
                                AND table_name = 'cihazlar' 
                                AND column_name = 'cihaz_tipi'
                            ) THEN
                                ALTER TABLE siramatik.cihazlar 
                                ADD COLUMN cihaz_tipi VARCHAR(50);
                            END IF;

                            -- kullanim_tipi kolonu yoksa ekle
                            IF NOT EXISTS (
                                SELECT 1 FROM information_schema.columns 
                                WHERE table_schema = 'siramatik' 
                                AND table_name = 'cihazlar' 
                                AND column_name = 'kullanim_tipi'
                            ) THEN
                                ALTER TABLE siramatik.cihazlar 
                                ADD COLUMN kullanim_tipi VARCHAR(50);
                            END IF;
                        END $$;
                    """))
                    session.commit()
                    print("[OK] Cihazlar tablosuna servis_id, kuyruk_id ve ip kolonlari kontrol edildi/eklendi!")
                except Exception as e:
                    print(f"[WARN] Kolon kontrol/ekleme hatasi: {e}")
                    session.rollback()
                return
            
            # Yeni tabloyu oluştur (IF NOT EXISTS ile)
            create_table_query = text("""
                CREATE TABLE IF NOT EXISTS siramatik.cihazlar (
                    id SERIAL PRIMARY KEY,
                    firma_id INTEGER NOT NULL REFERENCES siramatik.firmalar(id) ON DELETE CASCADE,
                    ad VARCHAR(255) NOT NULL,
                    cihaz_tipi VARCHAR(50),
                    kullanim_tipi VARCHAR(50),
                    device_fingerprint VARCHAR(500) UNIQUE,
                    mac_address VARCHAR(100),
                    ip VARCHAR(50),  -- Supabase'de 'ip' olarak tanımlı
                    durum VARCHAR(50) DEFAULT 'active' CHECK (durum IN ('active', 'inactive', 'maintenance')),
                    son_gorulen TIMESTAMP DEFAULT NOW(),
                    ayarlar JSONB DEFAULT '{}'::jsonb,
                    metadata JSONB DEFAULT '{}'::jsonb,
                    olusturulma TIMESTAMP DEFAULT NOW(),
                    guncelleme TIMESTAMP DEFAULT NOW(),
                    setup_tamamlandi BOOLEAN NOT NULL DEFAULT FALSE
                );
                
                CREATE INDEX IF NOT EXISTS idx_cihazlar_firma_id ON siramatik.cihazlar(firma_id);
                CREATE INDEX IF NOT EXISTS idx_cihazlar_kullanim_tipi ON siramatik.cihazlar(kullanim_tipi);
                CREATE INDEX IF NOT EXISTS idx_cihazlar_durum ON siramatik.cihazlar(durum);
                CREATE INDEX IF NOT EXISTS idx_cihazlar_fingerprint ON siramatik.cihazlar(device_fingerprint);
                CREATE INDEX IF NOT EXISTS idx_cihazlar_son_gorulen ON siramatik.cihazlar(son_gorulen);
                
                ALTER TABLE siramatik.cihazlar ENABLE ROW LEVEL SECURITY;
                
                DROP POLICY IF EXISTS cihazlar_select_policy ON siramatik.cihazlar;
                CREATE POLICY cihazlar_select_policy ON siramatik.cihazlar
                    FOR SELECT USING (true);
                
                DROP POLICY IF EXISTS cihazlar_insert_policy ON siramatik.cihazlar;
                CREATE POLICY cihazlar_insert_policy ON siramatik.cihazlar
                    FOR INSERT WITH CHECK (true);
                
                DROP POLICY IF EXISTS cihazlar_update_policy ON siramatik.cihazlar;
                CREATE POLICY cihazlar_update_policy ON siramatik.cihazlar
                    FOR UPDATE USING (true) WITH CHECK (true);
                
                DROP POLICY IF EXISTS cihazlar_delete_policy ON siramatik.cihazlar;
                CREATE POLICY cihazlar_delete_policy ON siramatik.cihazlar
                    FOR DELETE USING (true);
                
                COMMENT ON TABLE siramatik.cihazlar IS 'Tablet, Kiosk ve diğer cihazların kayıt ve yönetim tablosu';
            """)
            
            session.execute(create_table_query)
            session.commit()
            print("[OK] cihazlar tablosu (yeni yapi ile) olusturuldu!")
            
            # Servis ve Kuyruk ilişkilerini ekle (eğer yoksa)
            try:
                session.execute(text("""
                    DO $$ 
                    BEGIN
                        -- servis_id kolonu yoksa ekle
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.columns 
                            WHERE table_schema = 'siramatik' 
                            AND table_name = 'cihazlar' 
                            AND column_name = 'servis_id'
                        ) THEN
                            ALTER TABLE siramatik.cihazlar 
                            ADD COLUMN servis_id INTEGER REFERENCES siramatik.servisler(id) ON DELETE SET NULL;
                            CREATE INDEX IF NOT EXISTS idx_cihazlar_servis_id ON siramatik.cihazlar(servis_id);
                        END IF;
                        
                        -- kuyruk_id kolonu yoksa ekle
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.columns 
                            WHERE table_schema = 'siramatik' 
                            AND table_name = 'cihazlar' 
                            AND column_name = 'kuyruk_id'
                        ) THEN
                            ALTER TABLE siramatik.cihazlar 
                            ADD COLUMN kuyruk_id INTEGER REFERENCES siramatik.kuyruklar(id) ON DELETE SET NULL;
                            CREATE INDEX IF NOT EXISTS idx_cihazlar_kuyruk_id ON siramatik.cihazlar(kuyruk_id);
                        END IF;
                        
                        -- ip kolonu yoksa veya ip_address ise düzelt
                        IF EXISTS (
                            SELECT 1 FROM information_schema.columns 
                            WHERE table_schema = 'siramatik' 
                            AND table_name = 'cihazlar' 
                            AND column_name = 'ip_address'
                        ) AND NOT EXISTS (
                            SELECT 1 FROM information_schema.columns 
                            WHERE table_schema = 'siramatik' 
                            AND table_name = 'cihazlar' 
                            AND column_name = 'ip'
                        ) THEN
                            ALTER TABLE siramatik.cihazlar RENAME COLUMN ip_address TO ip;
                        END IF;
                        
                        -- ip kolonu yoksa ekle
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.columns 
                            WHERE table_schema = 'siramatik' 
                            AND table_name = 'cihazlar' 
                            AND column_name = 'ip'
                        ) THEN
                            ALTER TABLE siramatik.cihazlar 
                            ADD COLUMN ip VARCHAR(50);
                        END IF;
                    END $$;
                """))
                session.commit()
                print("[OK] Cihazlar tablosuna servis_id, kuyruk_id ve ip kolonlari eklendi/duzeltildi!")
            except Exception as e:
                print(f"[WARN] Kolon ekleme hatasi (zaten var olabilir): {e}")
                session.rollback()
            
        except Exception as e:
            print(f"[WARN] Cihazlar tablosu olusturma hatasi: {e}")
            session.rollback()
    
    def _create_cihaz_tipleri_table(self, session):
        """Cihaz tipi ve kullanım tipi referans tablosu"""
        try:
            create_table_query = text("""
                CREATE TABLE IF NOT EXISTS siramatik.cihaz_tipleri (
                    id SERIAL PRIMARY KEY,
                    kategori VARCHAR(20) NOT NULL CHECK (kategori IN ('cihaz', 'kullanim')),
                    kod VARCHAR(50) NOT NULL,
                    ad VARCHAR(100) NOT NULL,
                    aktif BOOLEAN NOT NULL DEFAULT TRUE,
                    olusturulma TIMESTAMP DEFAULT NOW(),
                    guncelleme TIMESTAMP DEFAULT NOW(),
                    CONSTRAINT uniq_cihaz_tipleri_kategori_kod UNIQUE (kategori, kod)
                );
            """)
            session.execute(create_table_query)
            session.commit()

            # Varsayılan kayıtlar (idempotent)
            seed_query = text("""
                INSERT INTO siramatik.cihaz_tipleri (kategori, kod, ad)
                VALUES 
                    -- Donanım tipleri
                    ('cihaz', 'TABLET', 'Tablet'),
                    ('cihaz', 'TV', 'TV / Monitör'),
                    ('cihaz', 'PC', 'PC / Dizüstü'),
                    ('cihaz', 'TELEFON', 'Telefon'),
                    ('cihaz', 'EL_MODULU', 'El Modülü'),
                    -- Kullanım tipleri
                    ('kullanim', 'KIOSK', 'Sıra Alma / Kiosk'),
                    ('kullanim', 'EKRAN', 'Sıra Ekranı'),
                    ('kullanim', 'KULLANICI_EKRANI', 'Personel / Kullanıcı Ekranı'),
                    ('kullanim', 'TELEFON', 'Telefon Uygulaması'),
                    ('kullanim', 'EL_MODULU', 'El Modülü')
                ON CONFLICT (kategori, kod) DO NOTHING;
            """)
            session.execute(seed_query)
            session.commit()
            print("[OK] cihaz_tipleri referans tablosu oluşturuldu / güncellendi")
        except Exception as e:
            print(f"[WARN] cihaz_tipleri tablosu olusturma / seed hatasi: {e}")
            session.rollback()
    
    def _backfill_device_types(self, session):
        """
        Eski kayıtlarda sadece tip kolonu dolu olabilir. tip kolonu varsa
        cihaz_tipi ve kullanim_tipi alanlarını tip değerine göre doldurur.
        Birden fazla kez çalıştırılsa da zararsızdır.
        """
        try:
            # tip kolonu var mı kontrol et
            check = session.execute(text("""
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'siramatik' AND table_name = 'cihazlar' AND column_name = 'tip'
            """)).first()
            if not check:
                return
            backfill_query = text("""
                UPDATE siramatik.cihazlar
                SET 
                    cihaz_tipi = COALESCE(
                        cihaz_tipi,
                        CASE 
                            WHEN tip IN ('kiosk','tablet') THEN 'TABLET'
                            WHEN tip = 'ekran' THEN 'TV'
                            WHEN tip = 'pc' THEN 'PC'
                            ELSE cihaz_tipi
                        END
                    ),
                    kullanim_tipi = COALESCE(
                        kullanim_tipi,
                        CASE 
                            WHEN tip IN ('kiosk','tablet') THEN 'KIOSK'
                            WHEN tip = 'ekran' THEN 'EKRAN'
                            WHEN tip = 'pc' THEN 'KULLANICI_EKRANI'
                            ELSE kullanim_tipi
                        END
                    )
                WHERE (cihaz_tipi IS NULL OR kullanim_tipi IS NULL)
                  AND tip IS NOT NULL;
            """)
            session.execute(backfill_query)
            session.commit()
            print("[OK] cihaz_tipi ve kullanim_tipi geriye dönük dolduruldu")
        except Exception as e:
            print(f"[WARN] cihaz_tipi/kullanim_tipi backfill hatasi: {e}")
            session.rollback()

    def _drop_cihazlar_tip_column(self, session):
        """cihazlar tablosundan eski tip kolonunu kaldır (migration)."""
        try:
            session.execute(text("ALTER TABLE siramatik.cihazlar DROP COLUMN IF EXISTS tip;"))
            session.execute(text("DROP INDEX IF EXISTS idx_cihazlar_tip;"))
            session.commit()
            print("[OK] cihazlar.tip kolonu kaldırıldı")
        except Exception as e:
            print(f"[WARN] cihazlar.tip kolonu kaldırılamadı: {e}")
            session.rollback()
    
    # ============================================
    # CİHAZ YÖNETİM METODLARI
    # Tüm cihaz zamanları (son_gorulen, guncelleme) ve online/offline kontrolü
    # get_local_now() kullanır; offset her zaman sistem_ayarlari.timezone_offset'tan okunur.
    # Sabit saat yok: 2, 3, 6, -5 vb. tablodaki değere göre değişir.
    # ============================================
    
    def register_device(self, firma_id: int, ad: str, tip: Optional[str] = None,
                       device_fingerprint: str = "", mac_address: Optional[str] = None,
                       ip: Optional[str] = None, ayarlar: Dict = {},
                       metadata: Dict = {}) -> Dict[str, Any]:
        """Yeni cihaz kaydı oluştur veya mevcut cihazı güncelle. Sadece cihaz_tipi ve kullanim_tipi kullanılır."""
        with Session(self.engine) as session:
            try:
                local_now = self.get_local_now()
                legacy_tip = (tip or "").lower()
                cihaz_tipi = None
                kullanim_tipi = None
                try:
                    if isinstance(metadata, dict):
                        cihaz_tipi = metadata.get("cihaz_tipi") or metadata.get("device_type")
                        kullanim_tipi = metadata.get("kullanim_tipi") or metadata.get("usage_type")
                except Exception:
                    pass
                if not cihaz_tipi:
                    if legacy_tip in ("kiosk", "tablet"): cihaz_tipi = "TABLET"
                    elif legacy_tip == "ekran": cihaz_tipi = "TV"
                    elif legacy_tip == "pc": cihaz_tipi = "PC"
                if not kullanim_tipi:
                    if legacy_tip in ("kiosk", "tablet"): kullanim_tipi = "KIOSK"
                    elif legacy_tip == "ekran": kullanim_tipi = "EKRAN"
                    elif legacy_tip == "pc": kullanim_tipi = "KULLANICI_EKRANI"

                check_query = text("""
                    SELECT id, firma_id FROM siramatik.cihazlar
                    WHERE device_fingerprint = :fingerprint
                """)
                result = session.execute(check_query, {"fingerprint": device_fingerprint}).first()
                
                if result:
                    device_id = result[0]
                    existing_firma_id = result[1]
                    if existing_firma_id != firma_id:
                        update_query = text(f"""
                            UPDATE siramatik.cihazlar
                            SET firma_id = :firma_id, ad = :ad,
                                cihaz_tipi = COALESCE(:cihaz_tipi, cihaz_tipi),
                                kullanim_tipi = COALESCE(:kullanim_tipi, kullanim_tipi),
                                ip = :ip, son_gorulen = {local_now}, guncelleme = {local_now}, durum = 'active'
                            WHERE id = :device_id
                            RETURNING id, firma_id, ad, durum, ayarlar, metadata
                        """)
                    else:
                        update_query = text(f"""
                            UPDATE siramatik.cihazlar
                            SET son_gorulen = {local_now}, durum = 'active', ip = COALESCE(:ip, ip)
                            WHERE id = :device_id
                            RETURNING id, firma_id, ad, durum, ayarlar, metadata
                        """)
                    result = session.execute(update_query, {
                        "device_id": device_id, "firma_id": firma_id, "ad": ad,
                        "cihaz_tipi": cihaz_tipi, "kullanim_tipi": kullanim_tipi, "ip": ip
                    }).first()
                    session.commit()
                    return {
                        "id": result[0], "firma_id": result[1], "ad": result[2],
                        "durum": result[3], "ayarlar": result[4] if result[4] else {},
                        "metadata": result[5] if result[5] else {}, "is_new": False
                    }
                
                insert_query = text(f"""
                    INSERT INTO siramatik.cihazlar 
                    (firma_id, ad, cihaz_tipi, kullanim_tipi, device_fingerprint, mac_address, ip, ayarlar, metadata, durum, son_gorulen, olusturulma, guncelleme)
                    VALUES (:firma_id, :ad, :cihaz_tipi, :kullanim_tipi, :fingerprint, :mac, :ip, :ayarlar, :metadata, 'active', {local_now}, {local_now}, {local_now})
                    RETURNING id, firma_id, ad, durum, ayarlar, metadata
                """)
                result = session.execute(insert_query, {
                    "firma_id": firma_id, "ad": ad, "cihaz_tipi": cihaz_tipi, "kullanim_tipi": kullanim_tipi,
                    "fingerprint": device_fingerprint, "mac": mac_address, "ip": ip,
                    "ayarlar": json.dumps(ayarlar), "metadata": json.dumps(metadata)
                }).first()
                session.commit()
                return {
                    "id": result[0], "firma_id": result[1], "ad": result[2],
                    "durum": result[3], "ayarlar": result[4] if result[4] else {},
                    "metadata": result[5] if result[5] else {}, "is_new": True
                }
                
            except Exception as e:
                session.rollback()
                raise Exception(f"Cihaz kayıt hatası: {str(e)}")
    
    def get_device_settings(self, device_id: int) -> Dict[str, Any]:
        """Cihaz ayarlarını getir"""
        with Session(self.engine) as session:
            query = text("""
                SELECT id, firma_id, ad, ayarlar, metadata, durum, son_gorulen,
                       setup_tamamlandi, cihaz_tipi, kullanim_tipi
                FROM siramatik.cihazlar
                WHERE id = :device_id
            """)
            result = session.execute(query, {"device_id": device_id}).first()
            
            if not result:
                raise Exception("Cihaz bulunamadı")
            
            return {
                "id": result[0],
                "firma_id": result[1],
                "ad": result[2],
                "ayarlar": result[3] if result[3] else {},
                "metadata": result[4] if result[4] else {},
                "durum": result[5],
                "son_gorulen": result[6],
                "setup_tamamlandi": result[7] if len(result) > 7 else False,
                "cihaz_tipi": result[8] if len(result) > 8 else None,
                "kullanim_tipi": result[9] if len(result) > 9 else None
            }
    
    def update_device_settings(self, device_id: int, ayarlar: Dict[str, Any], device_name: Optional[str] = None, setup_completed: Optional[bool] = None,
                               cihaz_tipi: Optional[str] = None, kullanim_tipi: Optional[str] = None) -> bool:
        """Cihaz ayarlarını güncelle (ayarlar JSON + opsiyonel cihaz adı, cihaz_tipi, kullanim_tipi + setup flag)"""
        with Session(self.engine) as session:
            try:
                local_now = self.get_local_now()
                
                # Önce mevcut cihazın setup durumunu kontrol et
                check_setup_query = text("""
                    SELECT setup_tamamlandi FROM siramatik.cihazlar WHERE id = :device_id
                """)
                setup_result = session.execute(check_setup_query, {"device_id": device_id}).first()
                existing_setup_completed = setup_result[0] if setup_result else False
                
                # Eğer setup zaten tamamlanmışsa saha tarafından gönderilen alanları ignore et (sadece admin değiştirebilir)
                if existing_setup_completed:
                    if device_name:
                        print(f"[SETUP] Cihaz {device_id} için setup tamamlanmış, device_name güncellemesi reddedildi")
                        device_name = None
                    if cihaz_tipi:
                        cihaz_tipi = None
                    if kullanim_tipi:
                        kullanim_tipi = None
                
                # Ayarlar içinden özet bölüm/kuyruk bilgisini çek (ilk seçilenler)
                servis_id = None
                kuyruk_id = None
                try:
                    if isinstance(ayarlar, dict):
                        servis_list = ayarlar.get("servisIds") or ayarlar.get("servis_ids")
                        kuyruk_list = ayarlar.get("kuyrukIds") or ayarlar.get("kuyruk_ids")
                        if isinstance(servis_list, list) and len(servis_list) > 0:
                            servis_id = int(servis_list[0])
                        if isinstance(kuyruk_list, list) and len(kuyruk_list) > 0:
                            kuyruk_id = int(kuyruk_list[0])
                except Exception:
                    # Sessizce geç, sadece özet kolonlar için
                    pass
                # setup_tamamlandi sadece explicit gelirse güncelle
                if setup_completed is None:
                    query = text(f"""
                        UPDATE siramatik.cihazlar
                        SET ayarlar = :ayarlar,
                            ad = COALESCE(:device_name, ad),
                            cihaz_tipi = COALESCE(:cihaz_tipi, cihaz_tipi),
                            kullanim_tipi = COALESCE(:kullanim_tipi, kullanim_tipi),
                            servis_id = COALESCE(:servis_id, servis_id),
                            kuyruk_id = COALESCE(:kuyruk_id, kuyruk_id),
                            guncelleme = {local_now}
                        WHERE id = :device_id
                        RETURNING id
                    """)
                    params = {
                        "device_id": device_id,
                        "ayarlar": json.dumps(ayarlar),
                        "device_name": device_name,
                        "cihaz_tipi": cihaz_tipi,
                        "kullanim_tipi": kullanim_tipi,
                        "servis_id": servis_id,
                        "kuyruk_id": kuyruk_id,
                    }
                else:
                    print(f"[SETUP] setup_tamamlandi güncelleniyor: device_id={device_id}, setup_tamamlandi={setup_completed}")
                    final_device_name = None if setup_completed else device_name
                    final_cihaz_tipi = None if setup_completed else cihaz_tipi
                    final_kullanim_tipi = None if setup_completed else kullanim_tipi
                    query = text(f"""
                        UPDATE siramatik.cihazlar
                        SET ayarlar = :ayarlar,
                            ad = COALESCE(:device_name, ad),
                            cihaz_tipi = COALESCE(:cihaz_tipi, cihaz_tipi),
                            kullanim_tipi = COALESCE(:kullanim_tipi, kullanim_tipi),
                            servis_id = COALESCE(:servis_id, servis_id),
                            kuyruk_id = COALESCE(:kuyruk_id, kuyruk_id),
                            setup_tamamlandi = :setup_tamamlandi,
                            guncelleme = {local_now}
                        WHERE id = :device_id
                        RETURNING id
                    """)
                    params = {
                        "device_id": device_id,
                        "ayarlar": json.dumps(ayarlar),
                        "device_name": final_device_name,
                        "cihaz_tipi": final_cihaz_tipi,
                        "kullanim_tipi": final_kullanim_tipi,
                        "servis_id": servis_id,
                        "kuyruk_id": kuyruk_id,
                        "setup_tamamlandi": setup_completed
                    }

                result = session.execute(query, params).first()
                
                session.commit()
                if result:
                    print(f"[OK] setup_tamamlandi başarıyla güncellendi: device_id={device_id}")
                return result is not None
                
            except Exception as e:
                session.rollback()
                raise Exception(f"Ayar güncelleme hatası: {str(e)}")
    
    def device_heartbeat(self, device_id: int, ip: Optional[str] = None,
                        metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Cihaz heartbeat güncelle (son_gorulen)"""
        local_now = self.get_local_now()
        with Session(self.engine) as session:
            try:
                query = text(f"""
                    UPDATE siramatik.cihazlar
                    SET son_gorulen = {local_now},
                        ip = COALESCE(:ip, ip),
                        metadata = COALESCE(:metadata, metadata),
                        durum = 'active'
                    WHERE id = :device_id
                    RETURNING id
                """)
                result = session.execute(query, {
                    "device_id": device_id,
                    "ip": ip,
                    "metadata": json.dumps(metadata) if metadata else None
                }).first()
                
                session.commit()
                return result is not None
                
            except Exception as e:
                session.rollback()
                raise Exception(f"Heartbeat hatası: {str(e)}")
    
    def get_devices_by_firma(self, firma_id: int) -> List[Dict[str, Any]]:
        """Firmaya ait tüm cihazları listele"""
        with Session(self.engine) as session:
            query = text(f"""
                SELECT 
                    c.id, c.firma_id, c.ad,
                    c.device_fingerprint, c.mac_address, c.ip,
                    c.durum, c.son_gorulen, c.ayarlar, c.metadata,
                    c.olusturulma, c.guncelleme, c.servis_id, c.kuyruk_id,
                    c.setup_tamamlandi, c.cihaz_tipi, c.kullanim_tipi,
                    s.ad as servis_ad, s.kod as servis_kod,
                    k.ad as kuyruk_ad, k.kod as kuyruk_kod,
                    CASE WHEN c.son_gorulen > {self._local_now_minus_interval("30 seconds")} THEN 'online' ELSE 'offline' END as online_status
                FROM siramatik.cihazlar c
                LEFT JOIN siramatik.servisler s ON c.servis_id = s.id
                LEFT JOIN siramatik.kuyruklar k ON c.kuyruk_id = k.id
                WHERE c.firma_id = :firma_id
                ORDER BY c.olusturulma DESC
            """)
            results = session.execute(query, {"firma_id": firma_id}).fetchall()
            
            devices = []
            for row in results:
                devices.append({
                    "id": row[0],
                    "firma_id": row[1],
                    "ad": row[2],
                    "device_fingerprint": row[3],
                    "mac_address": row[4],
                    "ip": row[5],
                    "durum": row[6],
                    "son_gorulen": row[7],
                    "ayarlar": row[8] if row[8] else {},
                    "metadata": row[9] if row[9] else {},
                    "olusturulma": row[10],
                    "guncelleme": row[11],
                    "servis_id": row[12],
                    "kuyruk_id": row[13],
                    "setup_tamamlandi": row[14],
                    "cihaz_tipi": row[15],
                    "kullanim_tipi": row[16],
                    "servis_ad": row[17],
                    "servis_kod": row[18],
                    "kuyruk_ad": row[19],
                    "kuyruk_kod": row[20],
                    "online_status": row[21]
                })
            
            return devices
    
    def delete_device(self, device_id: int) -> bool:
        """Cihazı sil"""
        with Session(self.engine) as session:
            try:
                query = text("""
                    DELETE FROM siramatik.cihazlar
                    WHERE id = :device_id
                    RETURNING id
                """)
                result = session.execute(query, {"device_id": device_id}).first()
                session.commit()
                return result is not None
                
            except Exception as e:
                session.rollback()
                raise Exception(f"Cihaz silme hatası: {str(e)}")
    
    def _create_rapor_sablonlari_table(self, session):
        """Rapor şablonları tablosunu oluştur"""
        try:
            check_query = text("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_schema = 'siramatik' 
                    AND table_name = 'rapor_sablonlari'
                );
            """)
            result = session.execute(check_query).scalar()
            
            if result:
                print("[OK] rapor_sablonlari tablosu zaten var")
                return
            
            create_table_query = text("""
                CREATE TABLE IF NOT EXISTS siramatik.rapor_sablonlari (
                    id SERIAL PRIMARY KEY,
                    firma_id INTEGER NOT NULL REFERENCES siramatik.firmalar(id) ON DELETE CASCADE,
                    kullanici_id INTEGER REFERENCES siramatik.kullanicilar(id) ON DELETE CASCADE,
                    ad VARCHAR(255) NOT NULL,
                    aciklama TEXT,
                    rapor_tipi VARCHAR(50) DEFAULT 'ag_grid',
                    ayarlar JSONB NOT NULL DEFAULT '{}'::jsonb,
                    varsayilan BOOLEAN DEFAULT FALSE,
                    olusturulma TIMESTAMPTZ DEFAULT NOW(),
                    guncelleme TIMESTAMPTZ DEFAULT NOW(),
                    CONSTRAINT unique_firma_sablon_ad UNIQUE(firma_id, ad)
                );
                
                CREATE INDEX IF NOT EXISTS idx_rapor_sablonlari_firma_id ON siramatik.rapor_sablonlari(firma_id);
                CREATE INDEX IF NOT EXISTS idx_rapor_sablonlari_kullanici_id ON siramatik.rapor_sablonlari(kullanici_id);
                CREATE INDEX IF NOT EXISTS idx_rapor_sablonlari_rapor_tipi ON siramatik.rapor_sablonlari(rapor_tipi);
                
                ALTER TABLE siramatik.rapor_sablonlari ENABLE ROW LEVEL SECURITY;
                
                DROP POLICY IF EXISTS rapor_sablonlari_select_policy ON siramatik.rapor_sablonlari;
                CREATE POLICY rapor_sablonlari_select_policy ON siramatik.rapor_sablonlari
                    FOR SELECT USING (true);
                
                DROP POLICY IF EXISTS rapor_sablonlari_insert_policy ON siramatik.rapor_sablonlari;
                CREATE POLICY rapor_sablonlari_insert_policy ON siramatik.rapor_sablonlari
                    FOR INSERT WITH CHECK (true);
                
                DROP POLICY IF EXISTS rapor_sablonlari_update_policy ON siramatik.rapor_sablonlari;
                CREATE POLICY rapor_sablonlari_update_policy ON siramatik.rapor_sablonlari
                    FOR UPDATE USING (true) WITH CHECK (true);
                
                DROP POLICY IF EXISTS rapor_sablonlari_delete_policy ON siramatik.rapor_sablonlari;
                CREATE POLICY rapor_sablonlari_delete_policy ON siramatik.rapor_sablonlari
                    FOR DELETE USING (true);
                
                COMMENT ON TABLE siramatik.rapor_sablonlari IS 'Kullanıcı rapor şablonları (AG-Grid vb.)';
            """)
            
            session.execute(create_table_query)
            session.commit()
            print("[OK] rapor_sablonlari tablosu oluşturuldu!")
            
        except Exception as e:
            print(f"[WARN] Rapor şablonları tablosu oluşturma hatası: {e}")
            session.rollback()
    
    # ============================================
    # RAPOR ŞABLONLARI METODLARI
    # ============================================
    
    def get_rapor_sablonlari(self, firma_id: int, kullanici_id: Optional[int] = None, 
                             rapor_tipi: str = 'ag_grid') -> List[Dict]:
        """Firma rapor şablonlarını getir"""
        query = """
            SELECT id, firma_id, kullanici_id, ad, aciklama, rapor_tipi, 
                   ayarlar, varsayilan, olusturulma, guncelleme
            FROM siramatik.rapor_sablonlari
            WHERE firma_id = :firma_id AND rapor_tipi = :rapor_tipi
        """
        params = {"firma_id": firma_id, "rapor_tipi": rapor_tipi}
        
        # Admin panelinde firmanın tüm şablonlarını göster
        # (kullanıcı bazlı filtreleme yapmıyoruz, tüm firma şablonları görünsün)
        # Eğer ileride kullanıcı bazlı filtreleme istenirse, bu kısım tekrar eklenebilir
        # if kullanici_id:
        #     query += " AND (kullanici_id = :kullanici_id OR kullanici_id IS NULL)"
        #     params["kullanici_id"] = kullanici_id
        
        query += " ORDER BY varsayilan DESC, ad ASC"
        
        return self.execute_query(query, params)
    
    def get_rapor_sablonu(self, sablon_id: int) -> Optional[Dict]:
        """Rapor şablonunu getir"""
        result = self.execute_query("""
            SELECT id, firma_id, kullanici_id, ad, aciklama, rapor_tipi, 
                   ayarlar, varsayilan, olusturulma, guncelleme
            FROM siramatik.rapor_sablonlari
            WHERE id = :sablon_id
        """, {"sablon_id": sablon_id})
        return result[0] if result else None
    
    def create_rapor_sablonu(self, firma_id: int, ad: str, ayarlar: Dict,
                            kullanici_id: Optional[int] = None,
                            aciklama: Optional[str] = None,
                            rapor_tipi: str = 'ag_grid',
                            varsayilan: bool = False) -> Dict:
        """Yeni rapor şablonu oluştur"""
        local_now = self.get_local_now()
        result = self.execute_query(f"""
            INSERT INTO siramatik.rapor_sablonlari 
            (firma_id, kullanici_id, ad, aciklama, rapor_tipi, ayarlar, varsayilan, olusturulma, guncelleme)
            VALUES (:firma_id, :kullanici_id, :ad, :aciklama, :rapor_tipi, :ayarlar, :varsayilan, {local_now}, {local_now})
            RETURNING *
        """, {
            "firma_id": firma_id,
            "kullanici_id": kullanici_id,
            "ad": ad,
            "aciklama": aciklama,
            "rapor_tipi": rapor_tipi,
            "ayarlar": json.dumps(ayarlar),
            "varsayilan": varsayilan
        })
        return result[0] if result else None
    
    def update_rapor_sablonu(self, sablon_id: int, ad: Optional[str] = None,
                            ayarlar: Optional[Dict] = None,
                            aciklama: Optional[str] = None,
                            varsayilan: Optional[bool] = None) -> Dict:
        """Rapor şablonunu güncelle"""
        local_now = self.get_local_now()
        fields = [f"guncelleme = {local_now}"]
        params = {"sablon_id": sablon_id}
        
        if ad is not None:
            fields.append("ad = :ad")
            params["ad"] = ad
        if ayarlar is not None:
            fields.append("ayarlar = :ayarlar")
            params["ayarlar"] = json.dumps(ayarlar)
        if aciklama is not None:
            fields.append("aciklama = :aciklama")
            params["aciklama"] = aciklama
        if varsayilan is not None:
            fields.append("varsayilan = :varsayilan")
            params["varsayilan"] = varsayilan
        
        query = f"""
            UPDATE siramatik.rapor_sablonlari 
            SET {', '.join(fields)}
            WHERE id = :sablon_id
            RETURNING *
        """
        result = self.execute_query(query, params)
        return result[0] if result else None
    
    def delete_rapor_sablonu(self, sablon_id: int) -> bool:
        """Rapor şablonunu sil"""
        self.execute_query("""
            DELETE FROM siramatik.rapor_sablonlari 
            WHERE id = :sablon_id
        """, {"sablon_id": sablon_id})
        return True

# Global database instance
db = Database()
