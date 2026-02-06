"""
Sıramatik - Ana FastAPI Uygulaması
Kuyruk Yönetim Sistemi - Sektör Agnostik
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uvicorn

from config import settings
from database import db
from auth import (
    create_access_token,
    verify_password,
    get_current_active_user,
)
from models import (
    LoginRequest,
    TokenResponse,
    SiraAlRequest,
    SiraAlResponse,
    SiraCagirRequest,
    SiraResponse,
    KuyrukResponse,
    KuyrukCreateRequest,
    ServisResponse,
    ServisCreateRequest,
    EkranCagriResponse,
    IstatistikResponse,
    DeviceResponse,
    DeviceUpdateRequest,
    UserResponse
)

# FastAPI uygulaması
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Queue Management System API - Sector Agnostic"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# HEALTH CHECK
# ============================================

@app.get("/")
async def root():
    """Ana endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "features": ["multi-queue", "vip-priority", "sector-agnostic"]
    }


@app.get("/health")
async def health_check():
    """Sağlık kontrolü"""
    return {"status": "healthy"}


# ============================================
# AUTH ENDPOINTS
# ============================================

@app.post("/api/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Kullanıcı girişi"""
    kullanici = db.get_user_by_email(request.email)
    
    if not kullanici:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email veya şifre hatalı"
        )
    
    if not verify_password(request.password, kullanici["sifre_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email veya şifre hatalı",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Token oluştur (UUID'yi string'e çevir)
    access_token = create_access_token(data={"sub": str(kullanici["id"])})
    kullanici_safe = {k: v for k, v in kullanici.items() if k != "sifre_hash"}
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "kullanici": kullanici_safe
    }


@app.get("/api/auth/me")
async def get_me(current_user: dict = Depends(get_current_active_user)):
    """Mevcut kullanıcı bilgisi"""
    kullanici_safe = {k: v for k, v in current_user.items() if k != "sifre_hash"}
    return kullanici_safe


# ============================================
# SIRA ENDPOINTS
# ============================================

@app.post("/api/sira/al", response_model=SiraAlResponse)
async def sira_al(request: SiraAlRequest):
    """
    Kiosk ekranından yeni sıra numarası al
    oncelik: 0 (normal) veya 1-9 (VIP)
    """
    try:
        # Kuyruk bilgisini al
        kuyruk = db.get_kuyruk(request.kuyruk_id)
        if not kuyruk:
            raise HTTPException(status_code=404, detail="Kuyruk bulunamadı")
        
        # Servis bilgisini al
        servis = db.get_servis(request.servis_id)
        if not servis:
            raise HTTPException(status_code=404, detail="Servis bulunamadı")
        
        # Yeni sıra oluştur
        sira = db.create_sira(
            request.kuyruk_id, 
            request.servis_id, 
            request.firma_id,
            request.oncelik
        )
        
        # Bekleyen sıra sayısını al
        bekleyen_sayisi = len(db.get_bekleyen_siralar(request.kuyruk_id))
        tahmini_bekleme = bekleyen_sayisi * 5  # Basit tahmin
        
        mesaj = f"{sira['numara']} numaralı sıranız alındı."
        if request.oncelik > 0:
            mesaj += " (Öncelikli sıra)"
        
        return SiraAlResponse(
            sira_id=sira["id"],
            numara=sira["numara"],
            tarih=sira["olusturulma"],
            kuyruk_ad=kuyruk["ad"],
            kuyruk_kod=kuyruk["kod"],
            bekleyen_sayisi=bekleyen_sayisi,
            tahmini_sure_dk=tahmini_bekleme if tahmini_bekleme > 0 else None,
            mesaj=mesaj
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sira/bekleyenler/{kuyruk_id}", response_model=List[SiraResponse])
async def bekleyen_siralar(
    kuyruk_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Staff panelinde bekleyen sıraları listele
    Öncelik sırasına göre (VIP önce)
    """
    siralar = db.get_bekleyen_siralar(kuyruk_id)
    return siralar


@app.get("/api/sira/bekleyen/{firma_id}", response_model=List[SiraResponse])
async def bekleyen_siralar_by_firma(
    firma_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Firmaya ait tüm bekleyen sıraları listele
    """
    siralar = db.get_tum_bekleyen_siralar(firma_id)
    print(f"\n[DEBUG] Bekleyenler: {siralar}\n")
    return siralar


@app.post("/api/sira/cagir/{sira_id}")
async def sira_cagir(
    sira_id: int,
    request: SiraCagirRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Staff sıradaki kişiyi çağırır
    """
    try:
        sira = db.cagir_sira(sira_id, request.kullanici_id, request.konum)
        
        if not sira:
            raise HTTPException(status_code=404, detail="Sıra bulunamadı")
        
        return {
            "success": True,
            "mesaj": f"{sira['numara']} numaralı sıra çağrıldı",
            "sira": sira
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/sira/tamamla/{sira_id}")
async def sira_tamamla(
    sira_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """
    İşlemi tamamla
    """
    try:
        sira = db.tamamla_sira(sira_id)
        
        if not sira:
            raise HTTPException(status_code=404, detail="Sıra bulunamadı")
        
        return {
            "success": True,
            "mesaj": "İşlem tamamlandı",
            "sira": sira
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# KUYRUK ENDPOINTS
# ============================================

@app.get("/api/kuyruklar/{servis_id}", response_model=List[KuyrukResponse])
async def kuyruk_listele(servis_id: int):
    """
    Kiosk ekranında kuyruk seçimi için
    Public endpoint
    """
    kuyruklar = db.get_kuyruklar(servis_id)
    
    result = []
    for kuyruk in kuyruklar:
        bekleyen = len(db.get_bekleyen_siralar(kuyruk["id"]))
        vip_bekleyen = len([s for s in db.get_bekleyen_siralar(kuyruk["id"]) if s.get("oncelik", 0) > 0])
        
        result.append({
            **kuyruk,
            "bekleyen_sayisi": bekleyen,
            "vip_bekleyen_sayisi": vip_bekleyen
        })
    
    return result


@app.get("/api/kuyruklar/firma/{firma_id}", response_model=List[KuyrukResponse])
async def kuyruk_listele_by_firma(firma_id: int):
    """Firmaya ait tüm kuyrukları listele"""
    kuyruklar = db.get_kuyruklar_by_firma(firma_id)
    result = []
    for kuyruk in kuyruklar:
        bekleyen = len(db.get_bekleyen_siralar(kuyruk["id"]))
        result.append({
            **kuyruk,
            "bekleyen_sayisi": bekleyen,
            "vip_bekleyen_sayisi": 0 
        })
    return result


@app.get("/api/kuyruklar/{id}", response_model=List[KuyrukResponse])
async def kuyruk_listele_generic(id: int):
    print(f"DEBUG: Kuyruk isteği geldi. ID: {id}")
    
    # Önce servis ID mi diye bak
    kuyruklar = db.get_kuyruklar(id)
    print(f"DEBUG: Servis ID ({id}) sorgusu sonucu (Yerel): {len(kuyruklar)} kayıt")
    
    if not kuyruklar:
        print(f"DEBUG: Servis bulunamadı, Firma ID olarak deneniyor: {id}")
        kuyruklar = db.get_kuyruklar_by_firma(id)
        print(f"DEBUG: Firma ID sorgusu sonucu: {len(kuyruklar)} kayıt")
        
    result = []
    for kuyruk in kuyruklar:
        bekleyen = len(db.get_bekleyen_siralar(kuyruk["id"]))
        # DEBUG LOG
        print(f"DEBUG: İşlenen Kuyruk: {kuyruk.get('ad')}, ID: {kuyruk.get('id')}, ServisID: {kuyruk.get('servis_id')}")
        
        result.append({
            **kuyruk,
            "bekleyen_sayisi": bekleyen,
            "vip_bekleyen_sayisi": 0
        })
        
    print(f"DEBUG: Dönen toplam sonuç: {len(result)}")
    return result


# ============================================
# SERVIS ENDPOINTS
# ============================================

@app.get("/api/servisler/{firma_id}", response_model=List[ServisResponse])
async def servis_listele(firma_id: int):
    """
    Firma servislerini listele
    Public endpoint
    """
    servisler = db.get_servisler(firma_id)
    
    result = []
    for servis in servisler:
        kuyruklar = db.get_kuyruklar(servis["id"])
        result.append({
            **servis,
            "kuyruk_sayisi": len(kuyruklar)
        })
    
    return result


# ============================================
# EKRAN ENDPOINTS
# ============================================

@app.get("/api/ekran/son-cagrilar/{firma_id}", response_model=List[EkranCagriResponse])
async def ekran_son_cagrilar(firma_id: int, limit: int = 5):
    """
    Ekranda son çağrılan numaraları göster
    Public endpoint
    """
    cagrilar = db.get_son_cagrilar(firma_id, limit)
    
    result = []
    for cagri in cagrilar:
        result.append({
            "numara": cagri["numara"],
            "kuyruk": cagri.get("kuyruk_ad", "Bilinmiyor"),
            "servis": cagri.get("servis_ad", "Bilinmiyor"),
            "konum": cagri.get("konum"),
            "oncelik": cagri.get("oncelik", 0),
            "cagirilma": cagri["cagirilma"]
        })
    
    return result


# ============================================
# ADMIN ENDPOINTS
# ============================================

@app.get("/api/admin/stats/{firma_id}", response_model=IstatistikResponse)
async def admin_stats(
    firma_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """Admin paneli için genel istatistikler"""
    stats = db.get_firma_istatistikleri(firma_id)
    return IstatistikResponse(
        toplam_sira=stats.get("toplam_sira", 0),
        vip_sira=stats.get("vip_sira", 0),
        bekleyen=stats.get("bekleyen", 0),
        cagirildi=stats.get("cagirildi", 0),
        tamamlandi=stats.get("tamamlandi", 0)
    )


@app.get("/api/admin/cihazlar/{firma_id}", response_model=List[dict])
async def admin_cihazlar(
    firma_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """Firmaya ait cihazları listele"""
    return db.get_cihazlar(firma_id)


@app.put("/api/admin/cihaz/{cihaz_id}")
async def update_cihaz(
    cihaz_id: int,
    request: DeviceUpdateRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """Cihaz bilgilerini güncelle (Bölüm/Hizmet ataması)"""
    update_data = request.model_dump(exclude_unset=True)
    cihaz = db.update_cihaz(cihaz_id, update_data)
    
    if not cihaz:
        raise HTTPException(status_code=404, detail="Cihaz bulunamadı")
        
    return {"success": True, "cihaz": cihaz}


# --- SERVIS CRUD ---

@app.post("/api/admin/servis")
async def create_servis(
    request: ServisCreateRequest,
    current_user: dict = Depends(get_current_active_user)
):
    return db.create_servis(request.firma_id, request.ad, request.kod, request.aciklama)

@app.put("/api/admin/servis/{servis_id}")
async def update_servis(
    servis_id: int,
    request: dict, # flexibility for partial updates
    current_user: dict = Depends(get_current_active_user)
):
    return db.update_servis(servis_id, request)

@app.delete("/api/admin/servis/{servis_id}")
async def delete_servis(
    servis_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    return db.delete_servis(servis_id)


# --- KUYRUK CRUD ---

@app.post("/api/admin/kuyruk")
async def create_kuyruk(
    request: KuyrukCreateRequest,
    current_user: dict = Depends(get_current_active_user)
):
    return db.create_kuyruk(request.servis_id, request.ad, request.kod, request.oncelik)

@app.put("/api/admin/kuyruk/{kuyruk_id}")
async def update_kuyruk(
    kuyruk_id: int,
    request: dict,
    current_user: dict = Depends(get_current_active_user)
):
    return db.update_kuyruk(kuyruk_id, request)

@app.delete("/api/admin/kuyruk/{kuyruk_id}")
async def delete_kuyruk(
    kuyruk_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    return db.delete_kuyruk(kuyruk_id)


# ============================================
# SUNUCU BAŞLATMA
# ============================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
