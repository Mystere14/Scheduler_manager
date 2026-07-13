"""
Configuration module for the application.
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    SECRETKEY: str = os.getenv("SECRETKEY", "dev-secret-key-change-me")
    ALGORITHM: str = "HS256"
    ACCESSTOKENEXPIREMINUTES: int = int(os.getenv("ACCESSTOKENEXPIREMINUTES", "1440"))  # 24h by default
    
    # Database configuration - Try multiple environment variable names for compatibility
    DATABASEURL = os.getenv(
        "DATABASEURL",
        os.getenv(
            "POSTGRESQLADDONURI",
            "postgresql+psycopg://admin:admin@localhost:5433/database",
        )
    )
    
    # Network / HTTP timeouts (seconds). Environment variables control these
    # values; naming convention: <DESCRIPTION>_<UNIT>. Use floats where
    # sub-second precision is useful.
    HTTPPINGTIMEOUTSECONDS: float = float(os.getenv("HTTPPINGTIMEOUTSECONDS", "2.0"))
    HTTPDATATIMEOUTSECONDS: float = float(os.getenv("HTTPDATATIMEOUTSECONDS", "5.0"))
    # Generic default for other HTTP calls that don't need a specialized timeout
    HTTPDEFAULTTIMEOUTSECONDS: float = float(os.getenv("HTTPDEFAULTTIMEOUTSECONDS", "5.0"))
    
    @property
    def accessTokenExpireDelta(self) -> timedelta:
        return timedelta(minutes=self.ACCESSTOKENEXPIREMINUTES)

settings = Settings()





