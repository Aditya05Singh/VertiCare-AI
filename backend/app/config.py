import os
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "VertiCare AI"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    
    # Security & JWT
    SECRET_KEY: str = "verticare-super-secret-production-grade-key-at-least-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours for prototype usability
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "verticare_user"
    POSTGRES_PASSWORD: str = "verticare_secure_pass"
    POSTGRES_DB: str = "verticare_db"
    
    # Database URLs (Defaulting to SQLite fallback for local test/dev if PostgreSQL not directly configured)
    DATABASE_URL: str = "sqlite+aiosqlite:///./verticare.db"
    SYNC_DATABASE_URL: str = "sqlite:///./verticare.db"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:8000"
    ]

    # ML & CV Storage Paths
    ML_MODEL_PATH: str = "ml/saved_models/verticare_xgb_v1.json"
    ML_SCALER_PATH: str = "ml/saved_models/verticare_scaler_v1.joblib"
    ML_METADATA_PATH: str = "ml/saved_models/model_metadata.json"

    # Medical Disclaimer Notice
    MEDICAL_DISCLAIMER: str = (
        "VertiCare AI is an academic prototype for vertigo screening and clinician decision support. "
        "It is NOT a diagnostic medical device and does NOT replace professional medical evaluation."
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
