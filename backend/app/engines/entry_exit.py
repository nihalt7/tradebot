from typing import Dict, Any
from datetime import datetime, timedelta

class EntryExitEngine:
    @staticmethod
    def calculate_levels(direction: str, current_price: float, atr: float, sr: Dict[str, float]) -> Dict[str, Any]:
        """
        Calculate realistic Entry Zone, Stop Loss, Target 1 (1:1.5), Target 2 (1:2.0), Target 3 (1:2.5+),
        and Risk/Reward metrics based on volatility (ATR 14) and support/resistance levels.
        """
        atr_buffered = max(current_price * 0.004, atr)  # At least 0.4% buffer

        if direction.upper() == "BUY":
            # Entry Zone: current price to +0.2%
            entry_min = round(current_price, 2)
            entry_max = round(current_price * 1.002, 2)
            
            # Stop loss: below recent support or 1.5 * ATR
            s1 = sr.get("support_1", current_price - (1.5 * atr_buffered))
            sl_candidate = max(current_price - (1.8 * atr_buffered), s1 * 0.998)
            stop_loss = round(min(sl_candidate, current_price - (0.8 * atr_buffered)), 2)
            
            risk = entry_min - stop_loss
            if risk <= 0:
                risk = atr_buffered * 1.2
                stop_loss = round(entry_min - risk, 2)

            # Targets based on R:R multiples
            t1 = round(entry_min + (1.5 * risk), 2)
            t2 = round(entry_min + (2.0 * risk), 2)
            t3 = round(entry_min + (2.8 * risk), 2)
            
            rr_ratio = round((t2 - entry_min) / (entry_min - stop_loss), 2)

        else:  # SELL
            entry_min = round(current_price * 0.998, 2)
            entry_max = round(current_price, 2)
            
            r1 = sr.get("resistance_1", current_price + (1.5 * atr_buffered))
            sl_candidate = min(current_price + (1.8 * atr_buffered), r1 * 1.002)
            stop_loss = round(max(sl_candidate, current_price + (0.8 * atr_buffered)), 2)
            
            risk = stop_loss - entry_max
            if risk <= 0:
                risk = atr_buffered * 1.2
                stop_loss = round(entry_max + risk, 2)

            t1 = round(entry_max - (1.5 * risk), 2)
            t2 = round(entry_max - (2.0 * risk), 2)
            t3 = round(entry_max - (2.8 * risk), 2)
            
            rr_ratio = round((entry_max - t2) / (stop_loss - entry_max), 2)

        now = datetime.now()
        expires_at = now + timedelta(minutes=5)  # 5-minute validity window
        max_holding_time = "Intraday (Square-off by 03:15 PM IST)"

        return {
            "entry_min": entry_min,
            "entry_max": entry_max,
            "stop_loss": stop_loss,
            "target_1": t1,
            "target_2": t2,
            "target_3": t3,
            "risk_amount_per_share": round(risk, 2),
            "risk_reward": rr_ratio,
            "validity_minutes": 5,
            "expires_at": expires_at,
            "max_holding": max_holding_time,
            "signal_time": now.strftime("%I:%M %p IST")
        }
