from typing import Dict, Any, Tuple

class SignalRankingEngine:
    """
    0-100 Technical Setup Score Engine adhering strictly to specifications:
    - Trend confirmation: 20
    - Volume confirmation: 20
    - RSI momentum: 10
    - VWAP confirmation: 10
    - MACD confirmation: 10
    - Price action: 15
    - Multi-timeframe confirmation: 10
    - Risk/reward quality: 5
    Total: 100
    """
    
    @staticmethod
    def calculate_score(
        indicators_primary: Dict[str, Any], # e.g. 5m
        indicators_higher: Dict[str, Any],  # e.g. 15m or 1h
        signal_type: str = "BUY",
        risk_reward_ratio: float = 2.0
    ) -> Tuple[int, Dict[str, int], str]:
        
        breakdown = {
            "trend": 0,
            "volume": 0,
            "rsi": 0,
            "vwap": 0,
            "macd": 0,
            "price_action": 0,
            "multi_timeframe": 0,
            "risk_reward": 0
        }
        
        price = indicators_primary.get("price", 0)
        ema9 = indicators_primary.get("ema9", 0)
        ema20 = indicators_primary.get("ema20", 0)
        ema50 = indicators_primary.get("ema50", 0)
        sma200 = indicators_primary.get("sma200", 0)
        supertrend_dir = indicators_primary.get("supertrend_direction", "")
        vol_ratio = indicators_primary.get("volume_ratio", 1.0)
        rsi = indicators_primary.get("rsi", 50)
        vwap = indicators_primary.get("vwap", 0)
        macd = indicators_primary.get("macd", 0)
        macd_signal = indicators_primary.get("macd_signal", 0)
        macd_hist = indicators_primary.get("macd_hist", 0)
        breakout = indicators_primary.get("breakout", False)
        breakdown_flag = indicators_primary.get("breakdown", False)
        pattern_bullish = indicators_primary.get("pattern_bullish", False)
        pattern_bearish = indicators_primary.get("pattern_bearish", False)
        
        higher_trend = indicators_higher.get("supertrend_direction", "")
        higher_rsi = indicators_higher.get("rsi", 50)
        
        if signal_type == "BUY":
            # 1. Trend confirmation (Max 20)
            trend_score = 0
            if ema9 > ema20 > ema50:
                trend_score += 10
            elif ema9 > ema20:
                trend_score += 6
            if price > sma200:
                trend_score += 5
            if supertrend_dir == "BULLISH":
                trend_score += 5
            breakdown["trend"] = min(20, trend_score)
            
            # 2. Volume confirmation (Max 20)
            if vol_ratio >= 2.0:
                breakdown["volume"] = 20
            elif vol_ratio >= 1.5:
                breakdown["volume"] = 16
            elif vol_ratio >= 1.2:
                breakdown["volume"] = 10
            elif vol_ratio >= 1.0:
                breakdown["volume"] = 5
            else:
                breakdown["volume"] = 0
                
            # 3. RSI Momentum (Max 10)
            # Bullish zone: 55 to 70 is ideal momentum; 50-55 moderate; >70 slightly overbought
            if 55 <= rsi <= 70:
                breakdown["rsi"] = 10
            elif 50 <= rsi < 55:
                breakdown["rsi"] = 7
            elif 70 < rsi <= 78:
                breakdown["rsi"] = 5
            else:
                breakdown["rsi"] = 2
                
            # 4. VWAP Confirmation (Max 10)
            if price > vwap:
                # Strong if bouncing off VWAP or within 1.5%
                dist = (price - vwap) / vwap
                if 0.0 <= dist <= 0.02:
                    breakdown["vwap"] = 10
                elif dist > 0:
                    breakdown["vwap"] = 8
            else:
                breakdown["vwap"] = 0
                
            # 5. MACD Confirmation (Max 10)
            if macd > macd_signal and macd_hist > 0:
                breakdown["macd"] = 10
            elif macd > macd_signal:
                breakdown["macd"] = 6
            else:
                breakdown["macd"] = 0
                
            # 6. Price Action (Max 15)
            pa_score = 0
            if breakout:
                pa_score += 10
            if pattern_bullish:
                pa_score += 5
            if not breakout and not pattern_bullish and price > ema9:
                pa_score += 4
            breakdown["price_action"] = min(15, pa_score)
            
            # 7. Multi-timeframe Confirmation (Max 10)
            mtf_score = 0
            if higher_trend == "BULLISH":
                mtf_score += 6
            if higher_rsi >= 50:
                mtf_score += 4
            breakdown["multi_timeframe"] = min(10, mtf_score)
            
            # 8. Risk / Reward Quality (Max 5)
            if risk_reward_ratio >= 2.5:
                breakdown["risk_reward"] = 5
            elif risk_reward_ratio >= 2.0:
                breakdown["risk_reward"] = 4
            elif risk_reward_ratio >= 1.5:
                breakdown["risk_reward"] = 2
            else:
                breakdown["risk_reward"] = 0

        else: # SELL / SHORT
            # 1. Trend confirmation (Max 20)
            trend_score = 0
            if ema9 < ema20 < ema50:
                trend_score += 10
            elif ema9 < ema20:
                trend_score += 6
            if price < sma200:
                trend_score += 5
            if supertrend_dir == "BEARISH":
                trend_score += 5
            breakdown["trend"] = min(20, trend_score)
            
            # 2. Volume confirmation (Max 20)
            if vol_ratio >= 2.0:
                breakdown["volume"] = 20
            elif vol_ratio >= 1.5:
                breakdown["volume"] = 16
            elif vol_ratio >= 1.2:
                breakdown["volume"] = 10
            elif vol_ratio >= 1.0:
                breakdown["volume"] = 5
            else:
                breakdown["volume"] = 0
                
            # 3. RSI Momentum (Max 10)
            # Bearish zone: 30 to 45 is ideal momentum
            if 30 <= rsi <= 45:
                breakdown["rsi"] = 10
            elif 45 < rsi <= 50:
                breakdown["rsi"] = 7
            elif 22 <= rsi < 30:
                breakdown["rsi"] = 5
            else:
                breakdown["rsi"] = 2
                
            # 4. VWAP Confirmation (Max 10)
            if price < vwap:
                dist = (vwap - price) / vwap
                if 0.0 <= dist <= 0.02:
                    breakdown["vwap"] = 10
                elif dist > 0:
                    breakdown["vwap"] = 8
            else:
                breakdown["vwap"] = 0
                
            # 5. MACD Confirmation (Max 10)
            if macd < macd_signal and macd_hist < 0:
                breakdown["macd"] = 10
            elif macd < macd_signal:
                breakdown["macd"] = 6
            else:
                breakdown["macd"] = 0
                
            # 6. Price Action (Max 15)
            pa_score = 0
            if breakdown_flag:
                pa_score += 10
            if pattern_bearish:
                pa_score += 5
            if not breakdown_flag and not pattern_bearish and price < ema9:
                pa_score += 4
            breakdown["price_action"] = min(15, pa_score)
            
            # 7. Multi-timeframe Confirmation (Max 10)
            mtf_score = 0
            if higher_trend == "BEARISH":
                mtf_score += 6
            if higher_rsi <= 50:
                mtf_score += 4
            breakdown["multi_timeframe"] = min(10, mtf_score)
            
            # 8. Risk / Reward Quality (Max 5)
            if risk_reward_ratio >= 2.5:
                breakdown["risk_reward"] = 5
            elif risk_reward_ratio >= 2.0:
                breakdown["risk_reward"] = 4
            elif risk_reward_ratio >= 1.5:
                breakdown["risk_reward"] = 2
            else:
                breakdown["risk_reward"] = 0
                
        total_score = sum(breakdown.values())
        total_score = max(0, min(100, total_score))
        
        if total_score >= 90:
            classification = "Excellent"
        elif total_score >= 80:
            classification = "Strong"
        elif total_score >= 70:
            classification = "Moderate"
        else:
            classification = "No alert"
            
        return total_score, breakdown, classification

ranking_engine = SignalRankingEngine()
