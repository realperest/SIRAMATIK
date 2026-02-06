"""
Sıramatik - Pydantic Modeller
Request/Response şemaları - Kuyruk Sistemi + VIP
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
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
    kuyruk_id: str
    servis_id: str
    firma_id: str
    oncelik: int = 0  # 0: Normal, 1-9: VIP


class SiraAlResponse(BaseModel):
    sira_id: str | uuid.UUID
    numara: str
    tarih: datetime
    kuyruk_ad: str
    kuyruk_kod: str
    bekleyen_sayisi: int
    tahmini_sure_dk: Optional[int] = None
    mesaj: str


class SiraCagirRequest(BaseModel):
    kullanici_id: str
    konum: Optional[str] = None  # Oda, gişe, masa no


class SiraResponse(BaseModel):
    id: str | uuid.UUID
    numara: str
    durum: str
    oncelik: int
    olusturulma: datetime
    cagirilma: Optional[datetime] = None


# --- KUYRUK MODELS ---

class KuyrukResponse(BaseModel):
    id: str | uuid.UUID
    servis_id: str | uuid.UUID # EKLENDİ
    ad: str
    kod: str
    aciklama: Optional[str] = None
    oncelik: int
    bekleyen_sayisi: Optional[int] = 0
    vip_bekleyen_sayisi: Optional[int] = 0

class KuyrukCreateRequest(BaseModel):
    servis_id: str
    ad: str
    kod: str
    oncelik: int = 0


# --- SERVIS MODELS ---

class ServisResponse(BaseModel):
    id: str | uuid.UUID
    ad: str
    kod: str
    aciklama: Optional[str] = None
    kuyruk_sayisi: Optional[int] = 0


class ServisCreateRequest(BaseModel):
    firma_id: str
    ad: str
    kod: str
    aciklama: Optional[str] = None


# --- EKRAN MODELS ---

class EkranCagriResponse(BaseModel):
    numara: str
    kuyruk: str
    servis: str
    konum: Optional[str] = None
    oncelik: int
    cagirilma: Optional[datetime] = None  # Boş olabilir

    model_config = ConfigDict(from_attributes=True)


# --- İSTATİSTİK MODELS ---

class IstatistikResponse(BaseModel):
    toplam_sira: int
    vip_sira: int
    bekleyen: int
    cagirildi: int
    tamamlandi: int
    ortalama_bekleme_dk: Optional[int] = None
