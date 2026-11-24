from datetime import datetime
from typing import Dict, List, Any, Optional
from app.services.market_data import IST
from app.services.risk_management import risk_management_service

class PaperTradingService:
    def __init__(self):
        self.virtual_capital: float = 1000000.0  # ₹10,00,000 INR
        self.available_balance: float = 1000000.0
        self.open_positions: Dict[str, Dict[str, Any]] = {}
        self.closed_positions: List[Dict[str, Any]] = []
        self.trade_history: List[Dict[str, Any]] = []

    def get_portfolio_summary(self, live_prices: Dict[str, float] = None) -> Dict[str, Any]:
        live_prices = live_prices or {}
        unrealized_pnl = 0.0
        invested_margin = 0.0
        
        positions_list = []
        for pos_id, pos in self.open_positions.items():
            sym = pos["symbol"]
            curr_price = live_prices.get(sym, pos["entry_price"])
            qty = pos["quantity"]
            side = pos["side"]
            entry = pos["entry_price"]
            
            if side == "BUY":
                pnl = (curr_price - entry) * qty
            else:
                pnl = (entry - curr_price) * qty
                
            pnl_pct = (pnl / (entry * qty)) * 100 if entry * qty > 0 else 0.0
            unrealized_pnl += pnl
            invested_margin += (entry * qty)
            
            pos_copy = dict(pos)
            pos_copy["current_price"] = curr_price
            pos_copy["unrealized_pnl"] = round(pnl, 2)
            pos_copy["unrealized_pnl_percent"] = round(pnl_pct, 2)
            positions_list.append(pos_copy)

        realized_pnl = sum(t["realized_pnl"] for t in self.closed_positions)
        total_pnl = realized_pnl + unrealized_pnl
        net_worth = self.virtual_capital + total_pnl
        
        win_trades = [t for t in self.closed_positions if t["realized_pnl"] > 0]
        loss_trades = [t for t in self.closed_positions if t["realized_pnl"] < 0]
        win_rate = (len(win_trades) / len(self.closed_positions) * 100) if self.closed_positions else 0.0
        
        return {
            "mode": "PAPER TRADING",
            "virtual_initial_capital": self.virtual_capital,
            "available_balance": round(self.available_balance, 2),
            "invested_margin": round(invested_margin, 2),
            "net_worth": round(net_worth, 2),
            "unrealized_pnl": round(unrealized_pnl, 2),
            "realized_pnl": round(realized_pnl, 2),
            "total_pnl": round(total_pnl, 2),
            "open_positions_count": len(positions_list),
            "closed_trades_count": len(self.closed_positions),
            "win_rate": round(win_rate, 2),
            "open_positions": positions_list,
            "closed_trades": self.closed_positions[-20:],
            "is_paper_trading": True
        }

    def execute_order(
        self,
        symbol: str,
        side: str,  # BUY or SELL
        quantity: int,
        price: float,
        stop_loss: Optional[float] = None,
        target: Optional[float] = None,
        signal_id: Optional[str] = None
    ) -> Dict[str, Any]:
        clean_sym = symbol.replace(".NS", "").replace(".BO", "").upper()
        now = datetime.now(IST)
        
        # Risk management pre-checks
        can_open = risk_management_service.can_open_position(len(self.open_positions))
        if not can_open["allowed"]:
            return {
                "success": False,
                "message": can_open["reason"],
                "is_paper_trading": True
            }
            
        trade_value = quantity * price
        charges = risk_management_service.estimate_indian_charges(trade_value, trade_value)
        
        if self.available_balance < trade_value:
            return {
                "success": False,
                "message": f"Insufficient paper trading funds. Required: ₹{round(trade_value, 2)}, Available: ₹{round(self.available_balance, 2)}",
                "is_paper_trading": True
            }
            
        pos_id = f"POS_{clean_sym}_{int(now.timestamp())}"
        position = {
            "id": pos_id,
            "symbol": clean_sym,
            "exchange": "NSE",
            "side": side,
            "quantity": quantity,
            "entry_price": round(price, 2),
            "stop_loss": round(stop_loss, 2) if stop_loss else None,
            "target": round(target, 2) if target else None,
            "signal_id": signal_id,
            "entry_time": now.strftime("%Y-%m-%d %H:%M:%S IST"),
            "estimated_entry_charges": charges["brokerage"] + charges["exchange_charges"],
            "status": "OPEN",
            "mode": "PAPER TRADING"
        }
        
        self.available_balance -= trade_value
        self.open_positions[pos_id] = position
        
        # Log to trade history
        self.trade_history.append({
            "id": f"ORD_{int(now.timestamp())}",
            "position_id": pos_id,
            "symbol": clean_sym,
            "action": side,
            "quantity": quantity,
            "price": round(price, 2),
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S IST"),
            "type": "PAPER_ORDER"
        })
        
        risk_management_service.settings["trades_today_count"] += 1
        
        return {
            "success": True,
            "message": f"Paper Trade Order executed successfully: {side} {quantity} {clean_sym} @ ₹{round(price, 2)}",
            "position": position,
            "is_paper_trading": True
        }

    def close_position(self, pos_id: str, exit_price: float, reason: str = "Manual Exit") -> Dict[str, Any]:
        if pos_id not in self.open_positions:
            return {"success": False, "message": "Position not found."}
            
        pos = self.open_positions.pop(pos_id)
        now = datetime.now(IST)
        
        qty = pos["quantity"]
        entry = pos["entry_price"]
        side = pos["side"]
        
        if side == "BUY":
            gross_pnl = (exit_price - entry) * qty
        else:
            gross_pnl = (entry - exit_price) * qty
            
        buy_val = (entry if side == "BUY" else exit_price) * qty
        sell_val = (exit_price if side == "BUY" else entry) * qty
        charges_dict = risk_management_service.estimate_indian_charges(buy_val, sell_val)
        charges = charges_dict["total_taxes_and_charges"]
        
        net_pnl = gross_pnl - charges
        
        # Return capital to balance
        self.available_balance += (entry * qty) + net_pnl
        
        closed_rec = {
            "id": pos["id"],
            "symbol": pos["symbol"],
            "side": side,
            "quantity": qty,
            "entry_price": entry,
            "exit_price": round(exit_price, 2),
            "gross_pnl": round(gross_pnl, 2),
            "charges": charges,
            "realized_pnl": round(net_pnl, 2),
            "pnl_percent": round((net_pnl / (entry * qty)) * 100, 2),
            "entry_time": pos["entry_time"],
            "exit_time": now.strftime("%Y-%m-%d %H:%M:%S IST"),
            "exit_reason": reason,
            "mode": "PAPER TRADING"
        }
        
        self.closed_positions.append(closed_rec)
        
        # Update daily risk tracking
        risk_management_service.settings["realized_daily_pnl"] += net_pnl
        if risk_management_service.settings["realized_daily_pnl"] <= -risk_management_service.settings["max_daily_loss"]:
            risk_management_service.settings["daily_loss_triggered"] = True
            
        return {
            "success": True,
            "message": f"Position closed for {pos['symbol']}. Realized P&L: ₹{round(net_pnl, 2)}",
            "trade": closed_rec,
            "is_paper_trading": True
        }

paper_trading_service = PaperTradingService()
