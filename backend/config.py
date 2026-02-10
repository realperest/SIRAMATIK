"""
Sıramatik - Konfigürasyon Ayarları
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Uygulama ayarları"""
    
    # Supabase (Opsiyonel - SQLite kullanıyoruz)
    SUPABASE_URL: str | None = None
    SUPABASE_KEY: str | None = None
    SUPABASE_SERVICE_KEY: str | None = None
    
    # JWT
    SECRET_KEY: str = "siramatik-secret-key-2024-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    
    # Uygulama
    APP_NAME: str = "Sıramatik"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # CORS - Tüm IP'lerden erişime izin ver (mobil cihazlar için)
    ALLOWED_ORIGINS: str = "*"
    
    @property
    def cors_origins(self) -> List[str]:
        """CORS origins listesi"""
        if self.ALLOWED_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"
    }


# Global settings instance
settings = Settings()
