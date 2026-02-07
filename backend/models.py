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
    email: EmailStr
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
    numara: str
    oncelik: int = 0
    notlar: Optional[str] = None

class SiraResponse(BaseModel):
    id: int
    numara: str
    durum: str
    oncelik: int
    olusturulma: datetime
    cagirilma: Optional[datetime] = None


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

class KuyrukCreateRequest(BaseModel):
    servis_id: int
    ad: str
    kod: str
    oncelik: int = 0


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
    konum: Optional[str] = None
    oncelik: int = 0
    cagirilma: Optional[datetime] = None

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
    aktif: Optional[bool] = None

# --- KULLANICI MODELS ---

class UserResponse(BaseModel):
    id: int
    firma_id: int
    email: str
    ad_soyad: str
    rol: str
    aktif: bool

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

class ServisCreateRequest(BaseModel):
    firma_id: int
    ad: str
    kod: Optional[str] = None
    aciklama: Optional[str] = None
    
class UserServisUpdateRequest(BaseModel):
    servis_id: Optional[int] = None
