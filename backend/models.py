"""
Sıramatik - Pydantic Modeller
Request/Response şemaları - Kuyruk Sistemi + VIP
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


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
    sira_id: str
    numara: str
    kuyruk_ad: str
    servis_ad: str
    oncelik: int
    tahmini_bekleme_dk: Optional[int] = None
    mesaj: str


class SiraCagirRequest(BaseModel):
    kullanici_id: str
    konum: Optional[str] = None  # Oda, gişe, masa no


class SiraResponse(BaseModel):
    id: str
    numara: str
    durum: str
    oncelik: int
    olusturulma: datetime
    cagirilma: Optional[datetime] = None


# --- KUYRUK MODELS ---

class KuyrukResponse(BaseModel):
    id: str
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
    aciklama: Optional[str] = None
    oncelik: int = 0


# --- SERVIS MODELS ---

class ServisResponse(BaseModel):
    id: str
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
    cagirilma: datetime


# --- İSTATİSTİK MODELS ---

class IstatistikResponse(BaseModel):
    toplam_sira: int
    vip_sira: int
    bekleyen: int
    cagirildi: int
    tamamlandi: int
    ortalama_bekleme_dk: Optional[int] = None
