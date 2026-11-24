import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Trade Bot - AI Indian Stock Market Engine"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "tradebot-super-secret-jwt-key-2026-production-nse")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # MongoDB Atlas
    MONGODB_URI: str = os.getenv("MONGODB_URI", "")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "tradebot_db")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://tradebot.vercel.app",
        "*"
    ]
    
    # Market Data
    MARKET_DATA_PROVIDER: str = os.getenv("MARKET_DATA_PROVIDER", "yfinance")
    SCANNER_INTERVAL_SECONDS: int = int(os.getenv("SCANNER_INTERVAL_SECONDS", "60"))
    DEFAULT_CAPITAL: float = float(os.getenv("DEFAULT_CAPITAL", "1000000.0"))
    RISK_PER_TRADE_PERCENT: float = float(os.getenv("RISK_PER_TRADE_PERCENT", "1.0"))
    MAX_DAILY_LOSS: float = float(os.getenv("MAX_DAILY_LOSS", "20000.0"))
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
