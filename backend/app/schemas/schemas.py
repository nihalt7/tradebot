from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# --- Auth Schemas ---
class UserBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class LoginRequest(BaseModel):
    username: str
    password: str

# --- Chat & Cards Schemas ---
class ChatMessageCreate(BaseModel):
    conversation_id: str = "main_chat"
    text: str

class SignalCardData(BaseModel):
    id: str
    symbol: str
    exchange: str = "NSE"
    signal: str  # "BUY" or "SELL"
    entry_min: float
    entry_max: float
    stop_loss: float
    target_1: float
    target_2: float
    target_3: float
    rsi: float
    vwap_status: str
    ema_status: str
    macd_status: str
    volume_ratio: float
    timeframe: str = "5 Minutes"
    setup_score: float
    risk_reward: str
    signal_time: str
    validity_minutes: int = 5
    reason: str
    suggested_qty: int = 0

class AnalysisCardData(BaseModel):
    symbol: str
    exchange: str = "NSE"
    current_price: float
    change_pct: float
    trend: str
    rsi_14: float
    supertrend: str
    supertrend_val: float
    vwap: float
    ema_9: float
    ema_20: float
    ema_50: float
    sma_200: float
    macd_bias: str
    support_1: float
    support_2: float
    resistance_1: float
    resistance_2: float
    candlestick_pattern: Optional[str] = None
    volume_surge: bool = False
    verdict: str
    score: float

class ChatMessageResponse(BaseModel):
    id: int
    conversation_id: str
    sender: str
    text: str
    message_type: str = "text"
    card_data: Optional[Dict[str, Any]] = None
    timestamp: datetime
    class Config:
        from_attributes = True

# --- Watchlist Schemas ---
class WatchlistAddRequest(BaseModel):
    symbol: str
    exchange: str = "NSE"
    notes: Optional[str] = None

class WatchlistItem(BaseModel):
    id: int
    symbol: str
    exchange: str
    company_name: str
    sector: Optional[str]
    current_price: float
    change_pct: float
    high: float
    low: float
    volume: float
    vwap: float
    trend: str
    added_at: datetime

# --- Scanner & Signal Schemas ---
class ScannerOpportunity(BaseModel):
    symbol: str
    exchange: str = "NSE"
    signal_type: str  # BUY or SELL
    current_price: float
    change_pct: float
    score: float
    volume_multiplier: float
    category: str  # "TOP_5_BUY", "TOP_5_SELL", "BREAKOUT", "BREAKDOWN", "VOLUME_SURGE", "MOMENTUM", "REVERSAL"
    entry_min: float
    entry_max: float
    stop_loss: float
    target_1: float
    target_2: float
    target_3: float
    risk_reward: float
    reason: str
    indicators: Dict[str, Any]

class ScannerResultsResponse(BaseModel):
    timestamp: str
    market_trend: str
    advances: int
    declines: int
    top_buys: List[ScannerOpportunity]
    top_sells: List[ScannerOpportunity]
    breakouts: List[ScannerOpportunity]
    breakdowns: List[ScannerOpportunity]
    volume_surges: List[ScannerOpportunity]

# --- Risk Management Schemas ---
class RiskSettingsUpdate(BaseModel):
    capital: float
    risk_per_trade_pct: float
    max_daily_loss: float
    max_open_trades: int
    paper_trading_enabled: bool

class RiskSettingsResponse(BaseModel):
    capital: float
    risk_per_trade_pct: float
    max_daily_loss: float
    current_daily_loss: float
    max_open_trades: int
    paper_trading_enabled: bool
    trading_halted: bool

# --- Order & Position Schemas ---
class PaperOrderRequest(BaseModel):
    symbol: str
    direction: str  # BUY or SELL
    quantity: int
    entry_price: float
    stop_loss: float
    target_1: float
    target_2: float
    target_3: float
    signal_id: Optional[str] = None

class ActivePositionResponse(BaseModel):
    id: int
    signal_id: Optional[str]
    symbol: str
    direction: str
    quantity: int
    entry_price: float
    current_price: float
    stop_loss: float
    target_1: float
    target_2: float
    target_3: float
    pnl: float
    pnl_percentage: float
    mode: str
    status: str
    opened_at: datetime

# --- Backtest Schemas ---
class BacktestRequest(BaseModel):
    symbol: str
    timeframe: str = "5m"
    days: int = 30
    capital: float = 500000.0
    risk_pct: float = 1.0

class BacktestResponse(BaseModel):
    symbol: str
    timeframe: str
    start_date: str
    end_date: str
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    profit_factor: float
    max_drawdown: float
    total_return_pct: float
    net_profit: float
    total_charges: float
    trades: List[Dict[str, Any]]
    equity_curve: List[Dict[str, Any]]
