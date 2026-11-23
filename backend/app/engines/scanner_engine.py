import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.app.market_data.provider_base import MarketDataProvider
from backend.app.market_data.universe import NSE_UNIVERSE
from backend.app.engines.technical_indicators import TechnicalIndicatorsEngine
from backend.app.engines.multi_timeframe import MultiTimeframeEngine
from backend.app.engines.ai_ranking import AIRankingEngine
from backend.app.engines.entry_exit import EntryExitEngine

logger = logging.getLogger(__name__)

class ScannerEngine:
    """ENGINE B: AUTOMATIC NSE MARKET SCANNER"""
    def __init__(self, provider: MarketDataProvider):
        self.provider = provider
        self.mtf_engine = MultiTimeframeEngine(provider)
        self.last_scan_time: Optional[datetime] = None
        self.cached_results: Dict[str, Any] = {
            "top_buys": [],
            "top_sells": [],
            "breakouts": [],
            "breakdowns": [],
            "volume_surges": [],
            "momentum_stocks": [],
            "reversals": [],
            "timestamp": "",
            "market_trend": "Neutral",
            "advances": 0,
            "declines": 0
        }

    def run_market_scan(self) -> Dict[str, Any]:
        """
        Execute full scan over the NSE equity universe.
        Computes technical indicators, ranks opportunities, categorizes them,
        and extracts Top 5 BUY, Top 5 SELL, Breakouts, Breakdowns, and Volume Surges.
        """
        all_buys: List[Dict[str, Any]] = []
        all_sells: List[Dict[str, Any]] = []
        breakouts: List[Dict[str, Any]] = []
        breakdowns: List[Dict[str, Any]] = []
        volume_surges: List[Dict[str, Any]] = []
        reversals: List[Dict[str, Any]] = []

        overview = self.provider.get_market_overview()
        advances = overview.get("advances", 0)
        declines = overview.get("declines", 0)
        market_trend = overview.get("market_trend", "Neutral")

        for item in NSE_UNIVERSE:
            sym = item["symbol"]
            try:
                quote = self.provider.get_quote(sym)
                df_5m = self.provider.get_historical_ohlcv(sym, timeframe="5m", limit=70)
                if len(df_5m) < 20:
                    continue

                ind = TechnicalIndicatorsEngine.compute_all_indicators(df_5m)
                mtf = self.mtf_engine.analyze_alignment(sym)
                current_price = ind.get("current_price", quote.get("price", 0.0))
                change_pct = quote.get("change_pct", 0.0)

                # Check Volume Surge
                vol_ratio = ind.get("volume_ratio", 1.0)
                if vol_ratio >= 1.6:
                    vol_item = {
                        "symbol": sym,
                        "name": item["name"],
                        "price": current_price,
                        "change_pct": change_pct,
                        "volume_multiplier": vol_ratio,
                        "trend": ind.get("supertrend_direction", "Neutral"),
                        "rsi": ind.get("rsi_14")
                    }
                    volume_surges.append(vol_item)

                # Check Breakout / Breakdown
                bo_info = ind.get("breakout", {})
                if bo_info.get("breakout"):
                    breakouts.append({
                        "symbol": sym,
                        "price": current_price,
                        "breakout_level": bo_info.get("breakout_level"),
                        "volume_multiplier": vol_ratio,
                        "change_pct": change_pct
                    })
                elif bo_info.get("breakdown"):
                    breakdowns.append({
                        "symbol": sym,
                        "price": current_price,
                        "breakdown_level": bo_info.get("breakdown_level"),
                        "volume_multiplier": vol_ratio,
                        "change_pct": change_pct
                    })

                # Evaluate BUY Opportunity
                levels_buy = EntryExitEngine.calculate_levels("BUY", current_price, ind.get("atr_14", 5.0), ind.get("support_resistance", {}))
                score_buy, breakdown_buy, tier_buy = AIRankingEngine.calculate_score("BUY", ind, mtf, levels_buy["risk_reward"])
                
                if score_buy >= 70.0 and tier_buy != "NO_ALERT":
                    all_buys.append({
                        "symbol": sym,
                        "name": item["name"],
                        "sector": item["sector"],
                        "signal_type": "BUY",
                        "current_price": current_price,
                        "change_pct": change_pct,
                        "score": score_buy,
                        "tier": tier_buy,
                        "volume_multiplier": vol_ratio,
                        "entry_min": levels_buy["entry_min"],
                        "entry_max": levels_buy["entry_max"],
                        "stop_loss": levels_buy["stop_loss"],
                        "target_1": levels_buy["target_1"],
                        "target_2": levels_buy["target_2"],
                        "target_3": levels_buy["target_3"],
                        "risk_reward": levels_buy["risk_reward"],
                        "category": "TOP_5_BUY",
                        "reason": f"Strong bullish momentum with {vol_ratio}x volume and multi-timeframe trend alignment.",
                        "indicators": ind
                    })

                # Evaluate SELL Opportunity
                levels_sell = EntryExitEngine.calculate_levels("SELL", current_price, ind.get("atr_14", 5.0), ind.get("support_resistance", {}))
                score_sell, breakdown_sell, tier_sell = AIRankingEngine.calculate_score("SELL", ind, mtf, levels_sell["risk_reward"])
                
                if score_sell >= 70.0 and tier_sell != "NO_ALERT":
                    all_sells.append({
                        "symbol": sym,
                        "name": item["name"],
                        "sector": item["sector"],
                        "signal_type": "SELL",
                        "current_price": current_price,
                        "change_pct": change_pct,
                        "score": score_sell,
                        "tier": tier_sell,
                        "volume_multiplier": vol_ratio,
                        "entry_min": levels_sell["entry_min"],
                        "entry_max": levels_sell["entry_max"],
                        "stop_loss": levels_sell["stop_loss"],
                        "target_1": levels_sell["target_1"],
                        "target_2": levels_sell["target_2"],
                        "target_3": levels_sell["target_3"],
                        "risk_reward": levels_sell["risk_reward"],
                        "category": "TOP_5_SELL",
                        "reason": f"Bearish breakdown with {vol_ratio}x volume expansion and downward Supertrend confirmation.",
                        "indicators": ind
                    })

            except Exception as e:
                logger.debug(f"Error scanning {sym}: {e}")
                continue

        # Sort descending by Setup Score
        all_buys.sort(key=lambda x: x["score"], reverse=True)
        all_sells.sort(key=lambda x: x["score"], reverse=True)
        volume_surges.sort(key=lambda x: x["volume_multiplier"], reverse=True)

        top_5_buys = all_buys[:5]
        top_5_sells = all_sells[:5]

        self.last_scan_time = datetime.now()
        self.cached_results = {
            "top_buys": top_5_buys,
            "top_sells": top_5_sells,
            "breakouts": breakouts[:5],
            "breakdowns": breakdowns[:5],
            "volume_surges": volume_surges[:6],
            "timestamp": self.last_scan_time.strftime("%I:%M:%S %p IST"),
            "market_trend": market_trend,
            "advances": advances,
            "declines": declines
        }

        return self.cached_results
