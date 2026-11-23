from typing import Dict, Any
from backend.app.engines.technical_indicators import TechnicalIndicatorsEngine
from backend.app.market_data.provider_base import MarketDataProvider

class MultiTimeframeEngine:
    def __init__(self, provider: MarketDataProvider):
        self.provider = provider

    def analyze_alignment(self, symbol: str) -> Dict[str, Any]:
        """
        Evaluate alignment across 5m (execution), 15m (trend), and 1h (macro) timeframes.
        Returns alignment metrics and trend score.
        """
        df_5m = self.provider.get_historical_ohlcv(symbol, timeframe="5m", limit=60)
        df_15m = self.provider.get_historical_ohlcv(symbol, timeframe="15m", limit=50)
        df_1h = self.provider.get_historical_ohlcv(symbol, timeframe="1h", limit=40)

        ind_5m = TechnicalIndicatorsEngine.compute_all_indicators(df_5m) if len(df_5m) >= 20 else {}
        ind_15m = TechnicalIndicatorsEngine.compute_all_indicators(df_15m) if len(df_15m) >= 15 else {}
        ind_1h = TechnicalIndicatorsEngine.compute_all_indicators(df_1h) if len(df_1h) >= 10 else {}

        bull_count = 0
        bear_count = 0

        # Check 5m
        if ind_5m:
            if ind_5m.get("supertrend_direction") == "Bullish" and ind_5m.get("current_price", 0) > ind_5m.get("vwap", 0):
                bull_count += 1
            elif ind_5m.get("supertrend_direction") == "Bearish" and ind_5m.get("current_price", 0) < ind_5m.get("vwap", 0):
                bear_count += 1

        # Check 15m
        if ind_15m:
            if ind_15m.get("supertrend_direction") == "Bullish" and ind_15m.get("rsi_14", 50) > 50:
                bull_count += 1
            elif ind_15m.get("supertrend_direction") == "Bearish" and ind_15m.get("rsi_14", 50) < 50:
                bear_count += 1

        # Check 1h
        if ind_1h:
            if ind_1h.get("supertrend_direction") == "Bullish":
                bull_count += 1
            elif ind_1h.get("supertrend_direction") == "Bearish":
                bear_count += 1

        is_bullish_aligned = (bull_count >= 2 and bear_count == 0)
        is_bearish_aligned = (bear_count >= 2 and bull_count == 0)

        return {
            "is_bullish_aligned": is_bullish_aligned,
            "is_bearish_aligned": is_bearish_aligned,
            "bull_votes": bull_count,
            "bear_votes": bear_count,
            "ind_5m": ind_5m,
            "ind_15m": ind_15m,
            "ind_1h": ind_1h
        }
