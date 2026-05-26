"""
Configuration module for the application.
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24h by default
    
    # Database configuration - Try multiple environment variable names for compatibility
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        os.getenv(
            "POSTGRESQL_ADDON_URI",
            "postgresql+psycopg://admin:admin@localhost:5433/database",
        )
    )
    
    # Network / HTTP timeouts (seconds). Environment variables control these
    # values; naming convention: <DESCRIPTION>_SECONDS. Use floats where
    # sub-second precision is useful.
    HTTP_PING_TIMEOUT_SECONDS: float = float(os.getenv("HTTP_PING_TIMEOUT_SECONDS", "2.0"))
    HTTP_DATA_TIMEOUT_SECONDS: float = float(os.getenv("HTTP_DATA_TIMEOUT_SECONDS", "5.0"))
    # Generic default for other HTTP calls that don't need a specialized timeout
    HTTP_DEFAULT_TIMEOUT_SECONDS: float = float(os.getenv("HTTP_DEFAULT_TIMEOUT_SECONDS", "5.0"))
    
    @property
    def access_token_expire_delta(self) -> timedelta:
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)

settings = Settings()





