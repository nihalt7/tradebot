from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from app.services.market_data import IST
from app.services.ranking_engine import ranking_engine

class OpportunityEngine:
    @staticmethod
    def generate_opportunity(
        symbol: str,
        indicators_primary: Dict[str, Any],
        indicators_higher: Dict[str, Any],
        timeframe: str = "5m",
        capital: float = 1000000.0,
        risk_percent: float = 1.0
    ) -> Optional[Dict[str, Any]]:
        
        price = indicators_primary.get("price", 0)
        atr = indicators_primary.get("atr", max(1.0, price * 0.008))
        if price <= 0:
            return None
            
        ema9 = indicators_primary.get("ema9", 0)
        ema20 = indicators_primary.get("ema20", 0)
        vwap = indicators_primary.get("vwap", 0)
        macd = indicators_primary.get("macd", 0)
        macd_sig = indicators_primary.get("macd_signal", 0)
        st_dir = indicators_primary.get("supertrend_direction", "")
        vol_ratio = indicators_primary.get("volume_ratio", 1.0)
        rsi = indicators_primary.get("rsi", 50)
        
        # Determine candidate direction
        bullish_triggers = (
            (price > vwap) and
            (ema9 >= ema20) and
            (macd >= macd_sig) and
            (st_dir == "BULLISH") and
            (rsi >= 50)
        )
        
        bearish_triggers = (
            (price < vwap) and
            (ema9 <= ema20) and
            (macd <= macd_sig) and
            (st_dir == "BEARISH") and
            (rsi <= 50)
        )
        
        if not bullish_triggers and not bearish_triggers:
            return None
            
        signal_type = "BUY" if bullish_triggers else "SELL"
        
        # Calculate SL & Targets based on ATR
        # Multipliers: SL = 1.5 ATR, T1 = 1.5 * Risk (R:R 1.5), T2 = 2.5 * Risk (R:R 2.5), T3 = 4.0 * Risk (R:R 4.0)
        risk_dist = max(atr * 1.2, price * 0.006)
        
        if signal_type == "BUY":
            entry_price = round(price, 2)
            stop_loss = round(entry_price - risk_dist, 2)
            target1 = round(entry_price + (risk_dist * 1.5), 2)
            target2 = round(entry_price + (risk_dist * 2.5), 2)
            target3 = round(entry_price + (risk_dist * 4.0), 2)
            rr_ratio = round((target2 - entry_price) / (entry_price - stop_loss), 2)
        else:
            entry_price = round(price, 2)
            stop_loss = round(entry_price + risk_dist, 2)
            target1 = round(entry_price - (risk_dist * 1.5), 2)
            target2 = round(entry_price - (risk_dist * 2.5), 2)
            target3 = round(entry_price - (risk_dist * 4.0), 2)
            rr_ratio = round((entry_price - target2) / (stop_loss - entry_price), 2)
            
        # Score calculation
        score, breakdown, classification = ranking_engine.calculate_score(
            indicators_primary=indicators_primary,
            indicators_higher=indicators_higher,
            signal_type=signal_type,
            risk_reward_ratio=rr_ratio
        )
        
        # Strictly adhere to: Below 70 = No alert!
        if score < 70:
            return None
            
        # Position sizing calculation
        risk_amount = capital * (risk_percent / 100.0)
        per_share_risk = abs(entry_price - stop_loss)
        quantity = int(risk_amount / per_share_risk) if per_share_risk > 0 else 1
        quantity = max(1, quantity)
        
        now = datetime.now(IST)
        expiration = now + timedelta(hours=3) # Valid for 3 hours or until market close
        
        clean_sym = symbol.replace(".NS", "").replace(".BO", "")
        
        # Rationale builder
        reasons = []
        if signal_type == "BUY":
            reasons.append(f"Price ₹{entry_price} trading comfortably above VWAP ₹{vwap}")
            reasons.append(f"Bullish EMA alignment (EMA9 ₹{ema9} > EMA20 ₹{ema20}) with Supertrend support")
            reasons.append(f"RSI({rsi}) showing strong upward momentum")
            if vol_ratio > 1.2:
                reasons.append(f"Volume surge at {vol_ratio}x 20-period average volume")
            if indicators_primary.get("breakout"):
                reasons.append("Clean 20-period price breakout confirmed")
        else:
            reasons.append(f"Price ₹{entry_price} rejected below VWAP ₹{vwap}")
            reasons.append(f"Bearish EMA alignment (EMA9 ₹{ema9} < EMA20 ₹{ema20}) with Supertrend resistance")
            reasons.append(f"RSI({rsi}) indicating persistent selling momentum")
            if vol_ratio > 1.2:
                reasons.append(f"High volume selloff at {vol_ratio}x 20-period average volume")
            if indicators_primary.get("breakdown"):
                reasons.append("Breakdown below recent key consolidation low")
                
        explanation = ". ".join(reasons) + "."
        
        return {
            "id": f"SIG_{clean_sym}_{int(now.timestamp())}",
            "symbol": clean_sym,
            "full_symbol": f"{clean_sym}.NS",
            "exchange": "NSE",
            "signal": signal_type,
            "setup_score": score,
            "classification": classification,
            "score_breakdown": breakdown,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "target1": target1,
            "target2": target2,
            "target3": target3,
            "risk_reward": rr_ratio,
            "recommended_quantity": quantity,
            "allocated_capital": round(quantity * entry_price, 2),
            "max_risk_amount": round(quantity * per_share_risk, 2),
            "timeframe": timeframe,
            "max_holding_period": "Intraday (Square off before 15:15 IST)",
            "signal_time": now.strftime("%Y-%m-%d %H:%M:%S IST"),
            "expiration_time": expiration.strftime("%Y-%m-%d %H:%M:%S IST"),
            "indicators": {
                "rsi": rsi,
                "vwap_status": "Bullish (Above)" if price > vwap else "Bearish (Below)",
                "ema_status": "Bullish" if ema9 > ema20 else "Bearish",
                "macd_status": "Bullish (Positive)" if macd > macd_sig else "Bearish",
                "volume_comparison": f"{vol_ratio}x 20-MA",
                "supertrend": st_dir
            },
            "explanation": explanation,
            "status": "ACTIVE"
        }

opportunity_engine = OpportunityEngine()
