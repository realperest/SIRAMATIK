"""
Sıramatik - Konfigürasyon Ayarları
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Uygulama ayarları"""
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: str
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    
    # Uygulama
    APP_NAME: str = "Sıramatik"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8080,http://127.0.0.1:3000,http://127.0.0.1:8080"
    
    @property
    def cors_origins(self) -> List[str]:
        """CORS origins listesi"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"
    }


# Global settings instance
settings = Settings()
