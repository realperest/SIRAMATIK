"""
Sıramatik - Ana FastAPI Uygulaması
Kuyruk Yönetim Sistemi - Sektör Agnostik
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import uvicorn

from config import settings
from database import db
from auth import (
    create_access_token,
    verify_password,
    get_password_hash,
    get_current_active_user,
    require_superadmin
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
    ServisCreateRequest,
    UserServisUpdateRequest,
    ServisResponse,
    ServisCreateRequest,
    EkranCagriResponse,
    ManuelSiraRequest,
    IstatistikResponse,
    DeviceResponse,
    DeviceUpdateRequest,
    DeviceHeartbeatRequest,
    UserResponse,
    UserCreateRequest,
    UserUpdateRequest
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
    """Kullanıcı girişi (Email veya Kullanıcı Adı)"""
    kullanici = db.find_user_by_login(request.login)
    
    if not kullanici:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Giriş bilgileri hatalı"
        )
    
    if not verify_password(request.password, kullanici["sifre_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Giriş bilgileri hatalı",
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


@app.get("/api/firma/{firma_id}")
async def get_firma_info(firma_id: int):
    """Firma genel bilgilerini getir (Public)"""
    firma = db.get_firma(firma_id)
    if not firma:
        raise HTTPException(status_code=404, detail="Firma bulunamadı")
    return firma


@app.get("/api/admin/all-firmalar")
async def get_all_firmalar_admin(_: dict = Depends(require_superadmin())):
    """Tüm firmaları getir (Sadece Süper Admin)"""
    return db.get_all_firmalar()

@app.post("/api/admin/firma")
async def create_firma_admin(
    request: dict,
    _: dict = Depends(require_superadmin())
):
    """Yeni firma oluşturma (Sadece Süper Admin)"""
    res = db.create_firma(request)
    if not res:
        raise HTTPException(status_code=400, detail="Firma oluşturulamadı")
    return res

@app.get("/api/admin/all-users")
async def get_all_users_admin(_: dict = Depends(require_superadmin())):
    """Sistemdeki tüm kullanıcıları getir (Sadece Süper Admin)"""
    return db.execute_query("""
        SELECT u.id, u.email, u.kullanici_adi, u.ad_soyad, u.rol, u.aktif, u.firma_id, f.ad as firma_ad
        FROM siramatik.kullanicilar u
        LEFT JOIN siramatik.firmalar f ON u.firma_id = f.id
        ORDER BY u.rol = 'superadmin' DESC, u.ad_soyad ASC
    """)

@app.put("/api/admin/firma/{firma_id}")
async def update_firma(
    firma_id: int, 
    data: dict, 
    current_user: dict = Depends(get_current_active_user)
):
    """Firma bilgilerini güncelle (Super Admin veya o firmanın Admin'i)"""
    user_rol = current_user.get("rol")
    user_firma_id = current_user.get("firma_id")
    
    # Yetki kontrolü
    if user_rol != "superadmin":
        if user_rol != "admin" or user_firma_id != firma_id:
             raise HTTPException(status_code=403, detail="Bu işlem için yetkiniz yok")
             
    # Veritabanı güncelleme
    res = db.update_firma(firma_id, data)
    if not res:
        raise HTTPException(status_code=400, detail="Firma bulunamadı veya güncelleme başarısız")
        
    return {"status": "success", "message": "Firma güncellendi", "id": firma_id}

# --- KULLANICI YÖNETİMİ (Süper Admin Paneli İçin) ---

@app.post("/api/admin/user")
async def create_user_admin(
    request: UserCreateRequest,
    current_user: dict = Depends(require_superadmin())
):
    """Sistem geneli kullanıcı oluştur (Sadece Süper Admin)"""
    # Şifreyi hashle
    hashed_password = get_password_hash(request.password)
    
    # Kullanıcıyı oluştur
@app.post("/api/admin/user")
async def create_user_admin(
    request: UserCreateRequest,
    current_user: dict = Depends(require_superadmin())
):
    """Sistem geneli kullanıcı oluştur (Sadece Süper Admin)"""
    # Şifreyi hashle
    hashed_password = get_password_hash(request.password)
    
    # Kullanıcıyı oluştur
    success = db.create_user(
        firma_id=request.firma_id,
        kullanici_adi=request.kullanici_adi,
        sifre_hash=hashed_password,
        ad_soyad=request.ad_soyad,
        ekran_ismi=request.ekran_ismi,
        email=request.email,
        rol=request.rol
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Kullanıcı adı veya email zaten kullanımda")
    return success

@app.put("/api/admin/user/{user_id}")
async def update_user_admin(
    user_id: int,
    request: dict,
    current_user: dict = Depends(require_superadmin())
):
    """Sistem geneli kullanıcı güncelle (Sadece Süper Admin)"""
    # Eğer şifre güncelleniyorsa hashle
    if "password" in request:
        request["sifre_hash"] = get_password_hash(request["password"])
        del request["password"]
        
    success = db.update_user(user_id, request)
    if not success:
        raise HTTPException(status_code=400, detail="Güncelleme başarısız")
    return success

@app.post("/api/auth/ekran-login")
async def ekran_login(request: dict):
    """Ekran müdahale şifresi ile firma tespiti"""
    sifre = request.get("sifre")
    if not sifre:
        raise HTTPException(status_code=400, detail="Şifre gerekli")
    
    firma = db.get_firma_by_ekran_sifre(sifre)
    if not firma:
        raise HTTPException(status_code=401, detail="Geçersiz müdahale şifresi")
    
    return {
        "firma_id": firma["id"],
        "firma_ad": firma["ad"],
        "status": "authorized"
    }

@app.get("/api/kiosk-config")
async def get_kiosk_config():
    """Kiosk için yerel ağ yapılandırmasını getir"""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    except:
        ip = "localhost"
    return {"host_ip": ip, "port": 3000} # Frontend portu 3000 genelde


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


@app.get("/api/sira/istatistik/gunluk/{firma_id}")
async def gunluk_istatistik(
    firma_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Günlük işlem sayılarını getir (Personel bazlı)"""
    # Eğer personel ise kendi yaptıklarını, admin ise hepsini mi?
    # Şimdilik sadece "kişisel performans" gösterelim.
    kullanici_id = str(current_user["id"])
    stats = db.get_gunluk_istatistik(firma_id, kullanici_id=kullanici_id)
    return stats
    
    
# --- ADMIN ENDPOINTS ---

@app.get("/api/admin/servisler/{firma_id}")
async def get_servisler(firma_id: str, _: dict = Depends(get_current_active_user)):
    return db.get_servisler_by_firma(firma_id)

# --- (Gereksiz Servis Create silindi) ---
# POST /api/admin/servis aşağıda tanımlı.

# Kullanıcı Yönetimi
@app.get("/api/admin/users/{firma_id}")
async def get_users(firma_id: str, _: dict = Depends(get_current_active_user)):
    return db.execute_query("""
        SELECT id, email, kullanici_adi, ad_soyad, rol, servis_id, varsayilan_kuyruk_id, varsayilan_konum_id, aktif 
        FROM siramatik.kullanicilar 
        WHERE firma_id = :firma_id
        ORDER BY ad_soyad
    """, {"firma_id": firma_id})

@app.put("/api/admin/user/{user_id}/servis")
async def update_user_servis(
    user_id: str, 
    data: UserServisUpdateRequest, 
    _: dict = Depends(get_current_active_user)
):
    success = db.update_user_servis(user_id, data.servis_id)
    if not success:
        raise HTTPException(status_code=400, detail="Güncelleme başarısız")
    return {"message": "Kullanıcı servisi güncellendi"} 

# KULLANICI CRUD
@app.post("/api/admin/user")
async def create_user(request: UserCreateRequest, _: dict = Depends(get_current_active_user)):
    # Kullanıcı adı çakışma kontrolü
    if request.kullanici_adi:
        if db.get_user_by_username(request.kullanici_adi):
            raise HTTPException(status_code=400, detail="Bu kullanıcı adı zaten kullanımda")
    else:
        # Default kullanıcı adı oluştur: Ad Soyad -> adsoyad (Türkçe karakter temizliği ile)
        tr_map = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
        base_username = request.ad_soyad.translate(tr_map).lower().replace(" ", "")
        # Sadece alfanümerik karakterleri tut
        base_username = "".join(c for c in base_username if c.isalnum())
        
        username = base_username
        counter = 1
        while db.get_user_by_username(username):
            username = f"{base_username}{counter}"
            counter += 1
        request.kullanici_adi = username

    # Email kontrolü (Opsiyonel olduğu için varsa kontrol et)
    if request.email:
        existing = db.get_user_by_email(request.email)
        if existing:
            raise HTTPException(status_code=400, detail="Bu email zaten kullanımda")
    
    sifre_hash = get_password_hash(request.password)
    user = db.create_user(
        kullanici_adi=request.kullanici_adi,
        email=request.email,
        ad_soyad=request.ad_soyad,
        sifre_hash=sifre_hash,
        firma_id=request.firma_id,
        rol=request.rol,
        servis_id=request.servis_id,
        varsayilan_kuyruk_id=request.varsayilan_kuyruk_id,
        varsayilan_konum_id=request.varsayilan_konum_id,
        aktif=request.aktif
    )
    if not user:
        raise HTTPException(status_code=400, detail="Kullanıcı oluşturulamadı")
    return user

@app.put("/api/admin/user/{user_id}")
async def update_user(user_id: int, request: UserUpdateRequest, _: dict = Depends(get_current_active_user)):
    update_data = request.model_dump(exclude_unset=True)
    user = db.update_user(user_id, update_data)
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    return user

@app.delete("/api/admin/user/{user_id}")
async def delete_user(user_id: int, _: dict = Depends(get_current_active_user)):
    db.delete_user(user_id)
    return {"message": "Kullanıcı silindi"}


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


@app.get("/api/kuyruklar/{kuyruk_id}/bekleyen-sayisi")
async def get_kuyruk_bekleyen_sayisi(kuyruk_id: int):
    """Bilet takibi için canlı bekleyen sayısı"""
    bekleyen = db.get_bekleyen_siralar(kuyruk_id)
    return {"sayi": len(bekleyen)}


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
async def ekran_son_cagrilar(firma_id: int, limit: int = 5, servis_id: Optional[int] = None):
    """
    Ekranda son çağrılan numaraları göster
    Public endpoint
    """
    print(f"DEBUG EKRAN QUERY START: firma={firma_id}")
    try:
        cagrilar = db.get_son_cagrilar(firma_id, limit, servis_id=servis_id)
        
        result = []
        for cagri in cagrilar:
            result.append({
                "id": cagri.get("id"),
                "numara": cagri.get("numara", "---"),
                "kuyruk": cagri.get("kuyruk_ad", "-"),
                "servis": cagri.get("servis_ad", "-"),
                "servis_id": cagri.get("servis_id"),
                "kuyruk_id": cagri.get("kuyruk_id"),
                "konum": cagri.get("konum"),
                "oncelik": cagri.get("oncelik", 0),
                "cagirilma": cagri.get("cagirilma")
            })
        
        return result
    except Exception as e:
        print(f"!!! EKRAN ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# ADMIN ENDPOINTS
# ============================================

@app.get("/api/admin/stats/{firma_id}", response_model=IstatistikResponse)
async def admin_stats(
    firma_id: int,
    servis_id: Optional[int] = None,
    period_type: str = "hour",
    time_range: str = "today",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user)
):
    """Admin paneli için genel istatistikler (Filtreli & Periyotlu)"""
    stats = db.get_firma_istatistikleri(
        firma_id, 
        servis_id=servis_id,
        period_type=period_type,
        time_range=time_range,
        start_date=start_date,
        end_date=end_date
    )
    return IstatistikResponse(
        toplam_sira=stats.get("toplam_sira", 0),
        vip_sira=stats.get("vip_sira", 0),
        bekleyen=stats.get("bekleyen", 0),
        cagirildi=stats.get("cagirildi", 0),
        tamamlandi=stats.get("tamamlandi", 0),
        ort_bekleme_dk=stats.get("ort_bekleme_dk", 0),
        ort_islem_dk=stats.get("ort_islem_dk", 0),
        hourly_labels=stats.get("hourly_labels", []),
        hourly_data=stats.get("hourly_data", []),
        service_labels=stats.get("service_labels", []),
        service_data=stats.get("service_data", []),
        recent_tickets=stats.get("recent_tickets", [])
    )


@app.post("/api/admin/cihaz/bildir")
async def cihaz_bildir(request: DeviceHeartbeatRequest):
    """Cihazdan gelen nabız sinyali"""
    cihaz = db.cihaz_bildir(request.firma_id, request.ad, request.tip, request.mac, request.metadata)
    return {"status": "ok", "cihaz": cihaz}


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



# --- MANUEL SIRA ---
@app.post("/api/admin/sira/manuel")
async def manuel_sira_al(request: ManuelSiraRequest, current_user: dict = Depends(get_current_active_user)):
    """Personel tarafından manuel sıra oluşturma"""
    sira = db.create_manuel_sira(
        kuyruk_id=request.kuyruk_id,
        servis_id=request.servis_id,
        firma_id=request.firma_id,
        numara=request.numara,
        oncelik=request.oncelik,
        notlar=request.notlar
    )
    if not sira:
        raise HTTPException(status_code=400, detail="Sıra oluşturulamadı")
    return sira

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
    return db.create_kuyruk(request.servis_id, request.ad, request.kod, request.oncelik, request.konumlar)

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
