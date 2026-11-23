from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import pandas as pd

class MarketDataProvider(ABC):
    @abstractmethod
    def get_quote(self, symbol: str) -> Dict[str, Any]:
        """Fetch real-time snapshot quote for a given NSE symbol."""
        pass

    @abstractmethod
    def get_historical_ohlcv(self, symbol: str, timeframe: str = "5m", limit: int = 100) -> pd.DataFrame:
        """Fetch historical OHLCV data bars."""
        pass

    @abstractmethod
    def get_market_overview(self) -> Dict[str, Any]:
        """Fetch index levels (NIFTY 50, BANK NIFTY, SENSEX), advances/declines, and market breadth."""
        pass
