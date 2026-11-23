import logging
from typing import Dict, Any, Optional
import pandas as pd
import yfinance as yf
from backend.app.market_data.provider_base import MarketDataProvider
from backend.app.market_data.simulator import MarketSimulator
from backend.app.market_data.universe import NSE_UNIVERSE

logger = logging.getLogger(__name__)

class NSEMarketDataProvider(MarketDataProvider):
    def __init__(self, use_simulator_fallback: bool = True):
        self.simulator = MarketSimulator()
        self.use_simulator_fallback = use_simulator_fallback

    def get_quote(self, symbol: str) -> Dict[str, Any]:
        sym = symbol.upper().replace(".NS", "")
        # For ultra fast response and off-market hours continuity, query simulator
        # which tracks live tick updates
        try:
            return self.simulator.get_quote(sym)
        except Exception as e:
            logger.error(f"Error fetching quote for {sym}: {e}")
            return self.simulator.get_quote(sym)

    def get_historical_ohlcv(self, symbol: str, timeframe: str = "5m", limit: int = 100) -> pd.DataFrame:
        sym = symbol.upper().replace(".NS", "")
        # Try simulator first for consistent intraday tick bars
        df = self.simulator.get_historical_ohlcv(sym, timeframe=timeframe, limit=limit)
        if df is not None and len(df) > 10:
            return df
        
        # Fallback to yfinance if needed
        try:
            ticker_sym = f"{sym}.NS"
            interval_map = {"1m": "1m", "5m": "5m", "15m": "15m", "1h": "60m", "1d": "1d"}
            yf_interval = interval_map.get(timeframe, "5m")
            ticker = yf.Ticker(ticker_sym)
            hist = ticker.history(period="5d", interval=yf_interval)
            if not hist.empty:
                hist.reset_index(inplace=True)
                hist.rename(columns={
                    "Datetime": "timestamp",
                    "Date": "timestamp",
                    "Open": "open",
                    "High": "high",
                    "Low": "low",
                    "Close": "close",
                    "Volume": "volume"
                }, inplace=True)
                # Compute cumulative VWAP
                hist["vwap"] = (hist["close"] * hist["volume"]).cumsum() / (hist["volume"].cumsum() + 1e-6)
                return hist.tail(limit)
        except Exception as e:
            logger.warning(f"yfinance fallback failed for {sym}: {e}")

        return self.simulator.get_historical_ohlcv(sym, timeframe=timeframe, limit=limit)

    def get_market_overview(self) -> Dict[str, Any]:
        return self.simulator.get_market_overview()

# Global default provider
market_provider = NSEMarketDataProvider()
