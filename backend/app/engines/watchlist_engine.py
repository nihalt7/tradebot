import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.app.market_data.provider_base import MarketDataProvider
from backend.app.engines.technical_indicators import TechnicalIndicatorsEngine
from backend.app.engines.multi_timeframe import MultiTimeframeEngine
from backend.app.engines.ai_ranking import AIRankingEngine
from backend.app.engines.entry_exit import EntryExitEngine

logger = logging.getLogger(__name__)

class WatchlistEngine:
    """ENGINE A: PERSONAL WATCHLIST MONITORING"""
    def __init__(self, provider: MarketDataProvider):
        self.provider = provider
        self.mtf_engine = MultiTimeframeEngine(provider)
        self.recent_alerts: Dict[str, datetime] = {}  # symbol -> last alert time

    def analyze_stock(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Analyze a single watched stock.
        Returns high-quality opportunity payload if score threshold met, else None (NO QUALITY OPPORTUNITY = NO MESSAGE).
        """
        try:
            quote = self.provider.get_quote(symbol)
            df_5m = self.provider.get_historical_ohlcv(symbol, timeframe="5m", limit=80)
            if len(df_5m) < 20:
                return None

            ind = TechnicalIndicatorsEngine.compute_all_indicators(df_5m)
            mtf = self.mtf_engine.analyze_alignment(symbol)
            current_price = ind.get("current_price", quote.get("price", 0.0))

            # Determine prospective direction
            bull_votes = (1 if ind.get("supertrend_direction") == "Bullish" else 0) + \
                         (1 if ind.get("current_price", 0) > ind.get("vwap", 0) else 0) + \
                         (1 if ind.get("rsi_14", 50) > 50 else 0) + \
                         (1 if mtf.get("is_bullish_aligned") else 0)

            bear_votes = (1 if ind.get("supertrend_direction") == "Bearish" else 0) + \
                         (1 if ind.get("current_price", 0) < ind.get("vwap", 0) else 0) + \
                         (1 if ind.get("rsi_14", 50) < 50 else 0) + \
                         (1 if mtf.get("is_bearish_aligned") else 0)

            direction = "BUY" if bull_votes >= 3 else ("SELL" if bear_votes >= 3 else None)
            if not direction:
                return None

            # Calculate prospective entry and exits
            levels = EntryExitEngine.calculate_levels(
                direction=direction,
                current_price=current_price,
                atr=ind.get("atr_14", current_price * 0.005),
                sr=ind.get("support_resistance", {})
            )

            score, breakdown, tier = AIRankingEngine.calculate_score(
                direction=direction,
                ind=ind,
                mtf=mtf,
                rr_ratio=levels["risk_reward"]
            )

            # Golden Rule Filter: Only alert if Setup Score >= 75 (Moderate to Excellent)
            if score < 75.0 or tier == "NO_ALERT":
                return None

            # Reason formulation
            reasons = []
            if breakdown["trend_confirmation"] >= 14:
                reasons.append(f"{direction} trend confirmed by Supertrend & EMAs")
            if breakdown["volume_confirmation"] >= 12:
                reasons.append(f"Volume surge {ind.get('volume_ratio')}x 20-MA")
            if breakdown["vwap_confirmation"] >= 7:
                reasons.append(f"Price holding firm {'above' if direction=='BUY' else 'below'} intraday VWAP")
            if mtf.get("is_bullish_aligned" if direction=="BUY" else "is_bearish_aligned"):
                reasons.append("Multi-timeframe trend alignment (5m, 15m, 1h)")

            reason_str = " | ".join(reasons) if reasons else "Multi-indicator quantitative confirmation."

            return {
                "source": "ENGINE_A_WATCHLIST",
                "symbol": symbol.upper(),
                "exchange": "NSE",
                "signal": direction,
                "entry_min": levels["entry_min"],
                "entry_max": levels["entry_max"],
                "stop_loss": levels["stop_loss"],
                "target_1": levels["target_1"],
                "target_2": levels["target_2"],
                "target_3": levels["target_3"],
                "risk_reward": f"1:{levels['risk_reward']}",
                "setup_score": score,
                "tier": tier,
                "rsi": ind.get("rsi_14"),
                "vwap_status": ind.get("vwap_status"),
                "ema_status": "Bullish" if ind.get("ema_bullish") else ("Bearish" if ind.get("ema_bearish") else "Neutral"),
                "macd_status": ind.get("macd_bias"),
                "volume_ratio": ind.get("volume_ratio"),
                "timeframe": "5 Minutes",
                "signal_time": levels["signal_time"],
                "validity_minutes": levels["validity_minutes"],
                "reason": reason_str,
                "breakdown": breakdown,
                "indicators": ind
            }
        except Exception as e:
            logger.error(f"WatchlistEngine error analyzing {symbol}: {e}")
            return None
