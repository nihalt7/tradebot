from datetime import datetime
from typing import Dict, Any, Optional

# MongoDB Collection Names
COLLECTION_USERS = "users"
COLLECTION_CONVERSATIONS = "conversations"
COLLECTION_CHAT_MESSAGES = "chat_messages"
COLLECTION_WATCHLISTS = "watchlists"
COLLECTION_STOCKS = "stocks"
COLLECTION_MARKET_DATA = "market_data"
COLLECTION_TECHNICAL_INDICATORS = "technical_indicators"
COLLECTION_TRADING_SIGNALS = "trading_signals"
COLLECTION_ACTIVE_POSITIONS = "active_positions"
COLLECTION_TRADING_HISTORY = "trading_history"
COLLECTION_RISK_SETTINGS = "risk_settings"
COLLECTION_BACKTEST_RESULTS = "backtest_results"
COLLECTION_NOTIFICATIONS = "notifications"
COLLECTION_API_CONFIGS = "api_configs"

def serialize_doc(doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Helper to ensure MongoDB document is JSON serializable."""
    if not doc:
        return None
    d = doc.copy()
    if "_id" in d:
        d["_id"] = str(d["_id"])
    return d
