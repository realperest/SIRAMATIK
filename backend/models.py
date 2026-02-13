"""
Sıramatik - Pydantic Modeller
Request/Response şemaları - Kuyruk Sistemi + VIP
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Any, Union, Dict
from datetime import datetime
import uuid


# --- AUTH MODELS ---

class LoginRequest(BaseModel):
    login: str # Email VEYA Kullanıcı Adı
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    kullanici: dict


# --- SIRA MODELS ---

class SiraAlRequest(BaseModel):
    kuyruk_id: int
    servis_id: int
    firma_id: int
    oncelik: int = 0  # 0: Normal, 1-9: VIP


class SiraAlResponse(BaseModel):
    sira_id: int
    numara: str
    tarih: datetime
    kuyruk_ad: str
    kuyruk_kod: str
    bekleyen_sayisi: int
    tahmini_sure_dk: Optional[int] = None
    mesaj: str


class SiraCagirRequest(BaseModel):
    kullanici_id: int
    konum: Optional[str] = None  # Oda, gişe, masa no


class ManuelSiraRequest(BaseModel):
    kuyruk_id: int
    servis_id: int
    firma_id: int
    numara: Optional[str] = None  # Boş veya sadece seri (X) ise backend günlük X001, X002... atar
    oncelik: int = 0
    notlar: Optional[str] = None

class SiraResponse(BaseModel):
    id: int
    numara: str
    durum: str
    oncelik: Optional[int] = 0
    olusturulma: datetime
    cagirilma: Optional[datetime] = None

    class Config:
        extra = "allow"


# --- KUYRUK MODELS ---

class KuyrukResponse(BaseModel):
    id: int
    servis_id: int
    ad: str
    kod: str
    aciklama: Optional[str] = None
    oncelik: int
    servis_ad: Optional[str] = None # EKLENDİ
    bekleyen_sayisi: Optional[int] = 0
    vip_bekleyen_sayisi: Optional[int] = 0
    konumlar: Optional[List[Dict[str, Any]]] = []

class KuyrukCreateRequest(BaseModel):
    servis_id: int
    ad: str
    kod: str
    oncelik: int = 0
    konumlar: Optional[List[Dict[str, Any]]] = []


# --- SERVIS MODELS ---

class ServisResponse(BaseModel):
    id: int
    ad: str
    kod: str
    aciklama: Optional[str] = None
    kuyruk_sayisi: Optional[int] = 0


class ServisCreateRequest(BaseModel):
    firma_id: int
    ad: str
    kod: str
    aciklama: Optional[str] = None


# --- EKRAN MODELS ---

class EkranCagriResponse(BaseModel):
    id: Any
    numara: str
    kuyruk: Optional[str] = "Bilinmiyor"
    servis: Optional[str] = "Bilinmiyor"
    servis_id: Optional[int] = None
    kuyruk_id: Optional[int] = None
    konum: Optional[str] = None
    oncelik: int = 0
    cagirilma: Optional[datetime] = None
    cagirilma_sayisi: int = 1

    model_config = ConfigDict(from_attributes=True)


# --- CİHAZ MODELS ---

class DeviceResponse(BaseModel):
    id: int
    firma_id: int
    servis_id: Optional[int] = None
    kuyruk_id: Optional[int] = None
    ad: str
    mac_adresi: Optional[str] = None
    tip: str  # 'button', 'kiosk', 'screen1', 'screen2', 'tablet', 'pc'
    konum: Optional[str] = None
    aktif: bool
    son_gorunme: Optional[datetime] = None

class DeviceUpdateRequest(BaseModel):
    servis_id: Optional[int] = None
    kuyruk_id: Optional[int] = None
    ad: Optional[str] = None
    konum: Optional[str] = None
    cihaz_tipi: Optional[str] = None
    kullanim_tipi: Optional[str] = None
    durum: Optional[str] = None
    aktif: Optional[bool] = None

# --- KULLANICI MODELS ---

class UserResponse(BaseModel):
    id: int
    firma_id: Optional[int] = None
    kullanici_adi: Optional[str] = None
    email: Optional[str] = None
    ad_soyad: str
    ekran_ismi: Optional[str] = None
    rol: str
    aktif: bool
    servis_id: Optional[int] = None
    varsayilan_kuyruk_id: Optional[int] = None
    varsayilan_konum_id: Optional[int] = None
    servis_ids: Optional[List[int]] = []
    kuyruk_ids: Optional[List[int]] = []
    durum: Optional[str] = "available"
    mola_nedeni: Optional[str] = None
    mola_baslangic: Optional[datetime] = None

class UserCreateRequest(BaseModel):
    firma_id: Optional[int] = None
    kullanici_adi: Optional[str] = None
    email: Optional[str] = None
    password: str
    ad_soyad: str
    ekran_ismi: Optional[str] = None
    rol: str = "staff" # 'admin', 'staff', 'superadmin' vb.
    varsayilan_konum_id: Optional[int] = None
    servis_ids: Optional[List[int]] = []
    kuyruk_ids: Optional[List[int]] = []
    aktif: bool = True

class UserUpdateRequest(BaseModel):
    kullanici_adi: Optional[str] = None
    email: Optional[str] = None
    ad_soyad: Optional[str] = None
    ekran_ismi: Optional[str] = None
    rol: Optional[str] = None
    servis_id: Optional[int] = None
    varsayilan_kuyruk_id: Optional[int] = None
    varsayilan_konum_id: Optional[int] = None
    servis_ids: Optional[List[int]] = None
    kuyruk_ids: Optional[List[int]] = None
    aktif: Optional[bool] = None

class UserStatusUpdateRequest(BaseModel):
    durum: str
    mola_nedeni: Optional[str] = None

class SiraTransferRequest(BaseModel):
    yeni_kuyruk_id: int
    yeni_servis_id: Optional[int] = None

class SiraNotlarRequest(BaseModel):
    notlar: str

class MemnuniyetAnketRequest(BaseModel):
    sira_id: int
    kuyruk_id: int
    servis_id: int
    firma_id: int
    cagiran_kullanici_id: Optional[int] = None
    puan: int  # 1-5 arası
    yorum: Optional[str] = None
    hizmet_suresi_dk: Optional[int] = None


# --- CİHAZ YÖNETİM MODELS ---

class CihazKayitRequest(BaseModel):
    firma_id: int
    ad: str  # Cihaz adı (örn: "Resepsiyon Tablet-1")
    tip: Optional[str] = None  # Eski/opsiyonel; cihaz_tipi/kullanim_tipi veya metadata kullanılır
    cihaz_tipi: Optional[str] = None  # TABLET, TV, PC, TELEFON, EL_MODULU
    kullanim_tipi: Optional[str] = None  # KIOSK, EKRAN, KULLANICI_EKRANI, TELEFON, EL_MODULU
    device_fingerprint: str  # Benzersiz browser fingerprint
    mac_address: Optional[str] = None
    ip: Optional[str] = None  # Supabase'de 'ip' kolonu
    ayarlar: Optional[Dict[str, Any]] = {}
    metadata: Optional[Dict[str, Any]] = {}


class CihazAyarlarUpdateRequest(BaseModel):
    ayarlar: Dict[str, Any]  # servis_ids, kuyruk_ids, hideServisSelection, vb.


class CihazHeartbeatRequest(BaseModel):
    device_id: int
    ip: Optional[str] = None  # Supabase'de 'ip' kolonu
    metadata: Optional[Dict[str, Any]] = None


class CihazResponse(BaseModel):
    id: int
    firma_id: int
    ad: str
    cihaz_tipi: Optional[str] = None
    kullanim_tipi: Optional[str] = None
    device_fingerprint: Optional[str] = None
    mac_address: Optional[str] = None
    ip: Optional[str] = None
    durum: str
    son_gorulen: datetime
    ayarlar: Dict[str, Any]
    metadata: Dict[str, Any]
    olusturulma: datetime
    guncelleme: datetime


# --- İSTATİSTİK MODELS ---

class IstatistikResponse(BaseModel):
    toplam_sira: int
    vip_sira: int
    bekleyen: int
    cagirildi: int
    tamamlandi: int
    ort_bekleme_dk: Optional[float] = 0
    ort_islem_dk: Optional[float] = 0
    hourly_labels: List[str] = []
    hourly_data: List[int] = []
    service_labels: List[str] = []
    service_data: List[int] = []
    recent_tickets: List[dict] = []

class DeviceHeartbeatRequest(BaseModel):
    firma_id: int
    ad: str
    tip: str
    mac: Optional[str] = None
    metadata: Optional[dict] = {}

class ServisCreateRequest(BaseModel):
    firma_id: int
    ad: str
    kod: Optional[str] = None
    aciklama: Optional[str] = None
    
class UserServisUpdateRequest(BaseModel):
    servis_id: Optional[int] = None


# --- RAPOR ŞABLONLARI MODELS ---

class RaporSablonuCreateRequest(BaseModel):
    firma_id: int
    ad: str
    ayarlar: Dict[str, Any]
    kullanici_id: Optional[int] = None
    aciklama: Optional[str] = None
    rapor_tipi: str = 'ag_grid'
    varsayilan: bool = False

class RaporSablonuUpdateRequest(BaseModel):
    ad: Optional[str] = None
    ayarlar: Optional[Dict[str, Any]] = None
    aciklama: Optional[str] = None
    varsayilan: Optional[bool] = None

class RaporSablonuResponse(BaseModel):
    id: int
    firma_id: int
    kullanici_id: Optional[int] = None
    ad: str
    aciklama: Optional[str] = None
    rapor_tipi: str
    ayarlar: Dict[str, Any]
    varsayilan: bool
    olusturulma: datetime
    guncelleme: datetime
