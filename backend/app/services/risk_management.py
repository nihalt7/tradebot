from typing import Dict, Any

class RiskManagementService:
    def __init__(self):
        self.settings = {
            "initial_capital": 1000000.0,
            "current_capital": 1000000.0,
            "risk_per_trade_percent": 1.0,
            "max_daily_loss": 20000.0,
            "max_trades_per_day": 8,
            "max_simultaneous_positions": 5,
            "slippage_percent": 0.05,
            "daily_loss_triggered": False,
            "trades_today_count": 0,
            "realized_daily_pnl": 0.0
        }

    def update_settings(self, new_settings: Dict[str, Any]) -> Dict[str, Any]:
        for k, v in new_settings.items():
            if k in self.settings:
                self.settings[k] = v
        return self.settings

    def get_settings(self) -> Dict[str, Any]:
        return self.settings

    def calculate_position_size(
        self,
        entry_price: float,
        stop_loss: float,
        capital: float = None,
        risk_percent: float = None
    ) -> Dict[str, Any]:
        cap = capital if capital is not None else self.settings["current_capital"]
        r_pct = risk_percent if risk_percent is not None else self.settings["risk_per_trade_percent"]
        
        risk_amount = cap * (r_pct / 100.0)
        per_share_risk = abs(entry_price - stop_loss)
        
        if per_share_risk <= 0:
            quantity = 1
        else:
            quantity = int(risk_amount / per_share_risk)
            
        quantity = max(1, quantity)
        total_trade_value = quantity * entry_price
        
        # Max position cap: not more than 25% capital in single stock
        max_allowed_val = cap * 0.25
        if total_trade_value > max_allowed_val and entry_price > 0:
            quantity = max(1, int(max_allowed_val / entry_price))
            total_trade_value = quantity * entry_price
            
        charges = self.estimate_indian_charges(total_trade_value, total_trade_value)
        
        return {
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "per_share_risk": round(per_share_risk, 2),
            "risk_amount": round(risk_amount, 2),
            "recommended_quantity": quantity,
            "total_trade_value": round(total_trade_value, 2),
            "estimated_charges": charges["total_taxes_and_charges"],
            "net_risk_with_charges": round(risk_amount + charges["total_taxes_and_charges"], 2)
        }

    def estimate_indian_charges(self, buy_value: float, sell_value: float) -> Dict[str, float]:
        """
        Calculates exact Indian equity intraday regulatory and broker charges:
        - Brokerage: ₹20 flat or 0.05% per executed order (whichever is lower)
        - STT (Securities Transaction Tax): 0.025% on sell side for equity intraday
        - Exchange Turnover Charges: 0.00325% on NSE turnover (buy + sell)
        - GST: 18% on (Brokerage + Exchange Turnover)
        - SEBI Charges: ₹10 per crore (0.0001%)
        - Stamp Duty: 0.003% on buy side
        - Slippage: 0.05% of turnover
        """
        turnover = buy_value + sell_value
        
        brokerage = min(20.0, buy_value * 0.0005) + min(20.0, sell_value * 0.0005)
        stt = sell_value * 0.00025
        exchange_charges = turnover * 0.0000325
        gst = (brokerage + exchange_charges) * 0.18
        sebi_charges = turnover * 0.000001
        stamp_duty = buy_value * 0.00003
        slippage = turnover * 0.0005
        
        total_statutory = stt + exchange_charges + gst + sebi_charges + stamp_duty
        total_all = brokerage + total_statutory + slippage
        
        return {
            "turnover": round(turnover, 2),
            "brokerage": round(brokerage, 2),
            "stt": round(stt, 2),
            "exchange_charges": round(exchange_charges, 2),
            "gst": round(gst, 2),
            "sebi_charges": round(sebi_charges, 2),
            "stamp_duty": round(stamp_duty, 2),
            "slippage_estimate": round(slippage, 2),
            "total_taxes_and_charges": round(total_all, 2)
        }

    def can_open_position(self, current_open_count: int, estimated_loss: float = 0.0) -> Dict[str, Any]:
        if self.settings["daily_loss_triggered"]:
            return {
                "allowed": False,
                "reason": f"Daily Circuit Breaker Triggered: Maximum daily loss ₹{self.settings['max_daily_loss']} reached. Trading halted for capital protection."
            }
            
        if self.settings["trades_today_count"] >= self.settings["max_trades_per_day"]:
            return {
                "allowed": False,
                "reason": f"Daily Trade Limit Reached: Max {self.settings['max_trades_per_day']} trades per day exceeded."
            }
            
        if current_open_count >= self.settings["max_simultaneous_positions"]:
            return {
                "allowed": False,
                "reason": f"Position Limit Reached: Maximum {self.settings['max_simultaneous_positions']} simultaneous positions open."
            }
            
        return {"allowed": True, "reason": "Risk checks passed."}

risk_management_service = RiskManagementService()
