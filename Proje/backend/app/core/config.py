"""
Application configuration using Pydantic Settings.
Optimized for performance and security.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings with validation."""
    
    # Application
    APP_NAME: str = "Gıda Nöbeti API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # OCR (will be used in TASK-BE-008)
    OCR_ENABLE_GPU: bool = False
    OCR_LANGUAGES: str = "tr,en"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Testing - pytest sırasında rate limit bypass
    TESTING: bool = False

    # Dashboard stats cache (Redis) - DEBUG=True olsa bile açılabilir
    DASHBOARD_CACHE_ENABLED: bool = True

    # Risk cron (TASK-BE-014) - her N saniyede bir tüm restoran risklerini güncelle
    RISK_CRON_ENABLED: bool = True
    RISK_CRON_INTERVAL_SECONDS: int = 3600  # 1 saat
    
    # Sentry (TASK-BE-019) - opsiyonel, boşsa devre dışı
    SENTRY_DSN: str | None = None
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables


# Global settings instance
settings = Settings()
