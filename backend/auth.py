"""
Sıramatik - Authentication & Authorization
JWT tabanlı basit auth sistemi
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import bcrypt
from config import settings
from database import db

# JWT Bearer token
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Şifreyi doğrula (bcrypt)"""
    try:
        if isinstance(plain_password, str):
            plain_password = plain_password.encode('utf-8')
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')
            
        return bcrypt.checkpw(plain_password, hashed_password)
    except Exception as e:
        print(f"Auth error: {e}")
        return False


def get_password_hash(password: str) -> str:
    """Şifreyi hashle (bcrypt)"""
    if isinstance(password, str):
        password = password.encode('utf-8')
    
    hashed = bcrypt.hashpw(password, bcrypt.gensalt())
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """JWT token oluştur"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """JWT token'ı decode et"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        print(f"DEBUG: JWT Hatası: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token geçersiz veya süresi dolmuş",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Mevcut kullanıcıyı getir (JWT'den)"""
    token = credentials.credentials
    payload = decode_token(token)
    
    kullanici_id: str = payload.get("sub")
    print(f"DEBUG: Token ID: {kullanici_id}, Tipi: {type(kullanici_id)}")
    
    if kullanici_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kullanıcı bilgisi bulunamadı"
        )
    
    kullanici = db.get_user_by_id(kullanici_id)
    print(f"DEBUG: Kullanıcı Bulundu mu?: {kullanici is not None}")
    
    if kullanici is None:
        print(f"DEBUG: Kullanıcı bulunamadı ID: {kullanici_id}") # Ekstra log
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kullanıcı bulunamadı"
        )
    
    return kullanici


async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    """Aktif kullanıcıyı getir"""
    # Veritabanında aktif kolonu yoksa varsayılan True kabul edelim
    if not current_user.get("aktif", True):
        raise HTTPException(status_code=400, detail="Kullanıcı aktif değil")
    return current_user


def require_role(required_role: str):
    """Belirli bir rol gerektir (decorator)"""
    async def role_checker(current_user: dict = Depends(get_current_active_user)):
        # Superadmin her şeyi yapabilir, admin ise kendi yetkilerini.
        user_rol = current_user.get("rol")
        if user_rol not in [required_role, "admin", "superadmin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Bu işlem için '{required_role}' yetkisi gerekli"
            )
        return current_user
    return role_checker

def require_superadmin():
    """Sadece Süper Admin erişimi"""
    async def checker(current_user: dict = Depends(get_current_active_user)):
        if current_user.get("rol") != "superadmin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bu sayfa sadece Süper Admin erişimine uygundur"
            )
        return current_user
    return checker
