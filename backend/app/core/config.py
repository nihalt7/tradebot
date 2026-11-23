import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "TradePulse AI - Indian Stock Market Quant Platform"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "tradepulse_super_secret_quant_key_2026_jwt_token_sign")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # MongoDB Atlas Configuration (Render / Atlas deployment)
    MONGODB_URI: str = os.getenv("MONGODB_URI", os.getenv("MONGODB_URL", ""))
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "tradepulse")
    
    # Render & Deployment Ports / CORS
    PORT: int = int(os.getenv("PORT", 8000))
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")
    
    # Market Trading Hours (Indian Standard Time)
    NSE_MARKET_OPEN_HOUR: int = 9
    NSE_MARKET_OPEN_MINUTE: int = 15
    NSE_MARKET_CLOSE_HOUR: int = 15
    NSE_MARKET_CLOSE_MINUTE: int = 30
    
    # Scanner Interval in seconds
    SCANNER_INTERVAL_SECONDS: int = 15
    WATCHLIST_MONITOR_INTERVAL_SECONDS: int = 10
    
    # Golden Rule Thresholds
    SETUP_SCORE_THRESHOLD: float = 75.0  # Alert threshold (70-79 Moderate, 80-89 Strong, 90-100 Excellent)
    MIN_RISK_REWARD_RATIO: float = 1.5
    
    # Default Risk Settings
    DEFAULT_CAPITAL: float = 500000.0  # ₹5,00,000
    DEFAULT_RISK_PER_TRADE_PCT: float = 1.0  # 1% per trade = ₹5,000
    DEFAULT_MAX_DAILY_LOSS: float = 15000.0  # ₹15,000 max daily loss
    DEFAULT_MAX_OPEN_TRADES: int = 5
    DEFAULT_PAPER_TRADING: bool = True

settings = Settings()
