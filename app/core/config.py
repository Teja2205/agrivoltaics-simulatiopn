import os
from typing import List, Optional, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Base directory and environment
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"
    
    # API settings
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Agrivoltaics Simulation API"
    VERSION: str = "1.0.0"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database settings
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://admin:Shadow2213@localhost:5432/agrivoltaics"
    )
    
    # CORS
    CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = [
        "http://localhost:3001",
        "http://localhost:8000",
        "http://localhost:8080",
    ]
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Weather API keys
    #WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "")
    WEATHER_API_PROVIDER: str = os.getenv("WEATHER_API_PROVIDER", "open-meteo")
    CACHE_WEATHER_DATA: bool = os.getenv("CACHE_WEATHER_DATA", "True").lower() == "true"
    
    # Machine learning models
    ML_MODELS_DIR: str = os.path.join(BASE_DIR, "models")
    USE_ML_MODELS: bool = os.getenv("USE_ML_MODELS", "True").lower() == "true"
    
    # Background tasks
    BACKGROUND_WORKERS: int = 4
    TASK_TIMEOUT_SECONDS: int = 3600  # 1 hour timeout for long-running tasks
    
    # Cache settings
    CACHE_DIR: str = os.path.join(BASE_DIR, "cache")
    CACHE_TTL_SECONDS: int = 60 * 60 * 24  # 1 day
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = os.path.join(BASE_DIR, "logs", "app.log")
    
    # Celery settings
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    
    # Model settings
    MODEL_PATH: str = os.path.join(BASE_DIR, "models")
    
    # Default simulation parameters
    DEFAULT_PANEL_EFFICIENCY: float = float(os.getenv("DEFAULT_PANEL_EFFICIENCY", "0.2"))
    DEFAULT_TRACKING_TYPE: str = os.getenv("DEFAULT_TRACKING_TYPE", "fixed")
    DEFAULT_CROP_TYPE: str = os.getenv("DEFAULT_CROP_TYPE", "lettuce")
    
    class Config:
        case_sensitive = True
        env_file = ".env"


# Create settings instance
settings = Settings()

# Create required directories
os.makedirs(os.path.join(settings.BASE_DIR, "logs"), exist_ok=True)
os.makedirs(os.path.join(settings.BASE_DIR, "cache"), exist_ok=True)
os.makedirs(settings.ML_MODELS_DIR, exist_ok=True)