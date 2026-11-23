from typing import Dict, Any, Tuple

class AIRankingEngine:
    @staticmethod
    def calculate_score(direction: str, ind: Dict[str, Any], mtf: Dict[str, Any], rr_ratio: float) -> Tuple[float, Dict[str, float], str]:
        """
        Calculate 0-100 Setup Quality Score based on 8 core quantitative criteria.
        Returns (total_score, breakdown_dict, tier_label).
        """
        breakdown = {
            "trend_confirmation": 0.0,         # Max 20
            "volume_confirmation": 0.0,        # Max 20
            "rsi_momentum": 0.0,              # Max 10
            "vwap_confirmation": 0.0,         # Max 10
            "macd_confirmation": 0.0,         # Max 10
            "price_action": 0.0,              # Max 15
            "multi_timeframe_alignment": 0.0, # Max 10
            "risk_reward_quality": 0.0        # Max 5
        }

        price = ind.get("current_price", 0.0)
        vwap = ind.get("vwap", 0.0)
        rsi = ind.get("rsi_14", 50.0)
        vol_ratio = ind.get("volume_ratio", 1.0)
        macd_hist = ind.get("macd_hist", 0.0)
        supertrend_dir = ind.get("supertrend_direction", "Neutral")
        candlestick = ind.get("candlestick", {})
        breakout = ind.get("breakout", {})

        if direction.upper() == "BUY":
            # 1. Trend confirmation (Max 20)
            if supertrend_dir == "Bullish" and ind.get("ema_bullish", False):
                breakdown["trend_confirmation"] = 20.0
            elif supertrend_dir == "Bullish" or ind.get("ema_9", 0) > ind.get("ema_20", 0):
                breakdown["trend_confirmation"] = 14.0
            elif ind.get("ema_9", 0) > ind.get("ema_20", 0):
                breakdown["trend_confirmation"] = 8.0

            # 2. Volume confirmation (Max 20)
            if vol_ratio >= 2.0:
                breakdown["volume_confirmation"] = 20.0
            elif vol_ratio >= 1.5:
                breakdown["volume_confirmation"] = 16.0
            elif vol_ratio >= 1.2:
                breakdown["volume_confirmation"] = 12.0
            elif vol_ratio >= 1.0:
                breakdown["volume_confirmation"] = 7.0

            # 3. RSI momentum (Max 10) - Sweet spot for intraday continuation is 55-68
            if 55.0 <= rsi <= 68.0:
                breakdown["rsi_momentum"] = 10.0
            elif 50.0 <= rsi < 55.0 or 68.0 < rsi <= 74.0:
                breakdown["rsi_momentum"] = 7.0
            elif 45.0 <= rsi < 50.0:
                breakdown["rsi_momentum"] = 4.0

            # 4. VWAP confirmation (Max 10)
            if price > vwap:
                distance_pct = ((price - vwap) / vwap) * 100
                if 0.1 <= distance_pct <= 1.5:
                    breakdown["vwap_confirmation"] = 10.0  # Healthy breakout above VWAP
                elif distance_pct > 1.5:
                    breakdown["vwap_confirmation"] = 7.0   # Slightly extended

            # 5. MACD confirmation (Max 10)
            if macd_hist > 0 and ind.get("macd", 0) > ind.get("macd_signal", 0):
                breakdown["macd_confirmation"] = 10.0
            elif macd_hist > 0:
                breakdown["macd_confirmation"] = 6.0

            # 6. Price action & Candlestick (Max 15)
            pa_score = 0.0
            if breakout.get("breakout"):
                pa_score += 9.0
            if candlestick.get("sentiment") == "Bullish":
                pa_score += 6.0
            elif candlestick.get("sentiment") == "Indecision":
                pa_score += 2.0
            breakdown["price_action"] = min(15.0, pa_score)

            # 7. Multi-timeframe confirmation (Max 10)
            if mtf.get("is_bullish_aligned"):
                breakdown["multi_timeframe_alignment"] = 10.0
            elif mtf.get("bull_votes", 0) >= 2:
                breakdown["multi_timeframe_alignment"] = 7.0
            elif mtf.get("bull_votes", 0) >= 1:
                breakdown["multi_timeframe_alignment"] = 4.0

        elif direction.upper() == "SELL":
            # 1. Trend confirmation (Max 20)
            if supertrend_dir == "Bearish" and ind.get("ema_bearish", False):
                breakdown["trend_confirmation"] = 20.0
            elif supertrend_dir == "Bearish" or ind.get("ema_9", 0) < ind.get("ema_20", 0):
                breakdown["trend_confirmation"] = 14.0
            elif ind.get("ema_9", 0) < ind.get("ema_20", 0):
                breakdown["trend_confirmation"] = 8.0

            # 2. Volume confirmation (Max 20)
            if vol_ratio >= 2.0:
                breakdown["volume_confirmation"] = 20.0
            elif vol_ratio >= 1.5:
                breakdown["volume_confirmation"] = 16.0
            elif vol_ratio >= 1.2:
                breakdown["volume_confirmation"] = 12.0
            elif vol_ratio >= 1.0:
                breakdown["volume_confirmation"] = 7.0

            # 3. RSI momentum (Max 10) - Bearish sweet spot 32-45
            if 32.0 <= rsi <= 45.0:
                breakdown["rsi_momentum"] = 10.0
            elif 45.0 < rsi <= 50.0 or 25.0 <= rsi < 32.0:
                breakdown["rsi_momentum"] = 7.0
            elif 50.0 < rsi <= 55.0:
                breakdown["rsi_momentum"] = 4.0

            # 4. VWAP confirmation (Max 10)
            if price < vwap:
                distance_pct = ((vwap - price) / vwap) * 100
                if 0.1 <= distance_pct <= 1.5:
                    breakdown["vwap_confirmation"] = 10.0
                elif distance_pct > 1.5:
                    breakdown["vwap_confirmation"] = 7.0

            # 5. MACD confirmation (Max 10)
            if macd_hist < 0 and ind.get("macd", 0) < ind.get("macd_signal", 0):
                breakdown["macd_confirmation"] = 10.0
            elif macd_hist < 0:
                breakdown["macd_confirmation"] = 6.0

            # 6. Price action & Candlestick (Max 15)
            pa_score = 0.0
            if breakout.get("breakdown"):
                pa_score += 9.0
            if candlestick.get("sentiment") == "Bearish":
                pa_score += 6.0
            elif candlestick.get("sentiment") == "Indecision":
                pa_score += 2.0
            breakdown["price_action"] = min(15.0, pa_score)

            # 7. Multi-timeframe confirmation (Max 10)
            if mtf.get("is_bearish_aligned"):
                breakdown["multi_timeframe_alignment"] = 10.0
            elif mtf.get("bear_votes", 0) >= 2:
                breakdown["multi_timeframe_alignment"] = 7.0
            elif mtf.get("bear_votes", 0) >= 1:
                breakdown["multi_timeframe_alignment"] = 4.0

        # 8. Risk / Reward quality (Max 5)
        if rr_ratio >= 2.5:
            breakdown["risk_reward_quality"] = 5.0
        elif rr_ratio >= 2.0:
            breakdown["risk_reward_quality"] = 4.0
        elif rr_ratio >= 1.5:
            breakdown["risk_reward_quality"] = 3.0
        else:
            breakdown["risk_reward_quality"] = 1.0

        total_score = round(sum(breakdown.values()), 1)

        # Tier classification
        if total_score >= 90.0:
            tier = "EXCELLENT"
        elif total_score >= 80.0:
            tier = "STRONG"
        elif total_score >= 70.0:
            tier = "MODERATE"
        else:
            tier = "NO_ALERT"

        return total_score, breakdown, tier
