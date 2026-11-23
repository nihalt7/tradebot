import math
from typing import Dict, Any, Tuple

class RiskManager:
    @staticmethod
    def calculate_position_size(capital: float, risk_per_trade_pct: float, entry_price: float, stop_loss: float) -> int:
        """
        Calculate maximum allowable share quantity strictly adhering to fixed fractional risk.
        Quantity = floor((Capital * Risk%) / abs(Entry - StopLoss))
        """
        risk_per_share = abs(entry_price - stop_loss)
        if risk_per_share <= 0:
            return 1
            
        max_monetary_risk = capital * (risk_per_trade_pct / 100.0)
        raw_quantity = max_monetary_risk / risk_per_share
        
        # Capital constraint: cannot allocate more than 30% of total capital into a single stock
        max_capital_qty = (capital * 0.30) / entry_price
        
        quantity = int(math.floor(min(raw_quantity, max_capital_qty)))
        return max(1, quantity)

    @staticmethod
    def calculate_indian_statutory_charges(direction: str, quantity: int, entry_price: float, exit_price: float) -> Dict[str, float]:
        """
        Accurately calculate Indian equity intraday statutory and broker charges:
        1. Brokerage: ₹20 or 0.03% (whichever lower) each side = max ₹40
        2. STT (Securities Transaction Tax): 0.025% on Sell side only
        3. Exchange Turnover Charge: 0.00325% of total turnover (Buy + Sell)
        4. SEBI Turnover Fee: ₹10 per crore (0.0001%) of turnover
        5. GST: 18% on (Brokerage + Exchange Charges + SEBI Charges)
        6. Stamp Duty: 0.003% on Buy side turnover
        7. Slippage estimate: 0.05%
        """
        buy_price = entry_price if direction == "BUY" else exit_price
        sell_price = exit_price if direction == "BUY" else entry_price

        buy_turnover = buy_price * quantity
        sell_turnover = sell_price * quantity
        total_turnover = buy_turnover + sell_turnover

        # 1. Brokerage
        brokerage_buy = min(20.0, buy_turnover * 0.0003)
        brokerage_sell = min(20.0, sell_turnover * 0.0003)
        total_brokerage = round(brokerage_buy + brokerage_sell, 2)

        # 2. STT
        stt = round(sell_turnover * 0.00025, 2)

        # 3. Exchange turnover charges (NSE ~0.00325%)
        exchange_charges = round(total_turnover * 0.0000325, 2)

        # 4. SEBI charges
        sebi_charges = round(total_turnover * 0.000001, 2)

        # 5. GST (18%)
        gst = round(0.18 * (total_brokerage + exchange_charges + sebi_charges), 2)

        # 6. Stamp Duty
        stamp_duty = round(buy_turnover * 0.00003, 2)

        # 7. Slippage
        slippage = round(total_turnover * 0.0005, 2)

        total_taxes_and_charges = round(total_brokerage + stt + exchange_charges + sebi_charges + gst + stamp_duty, 2)

        return {
            "brokerage": total_brokerage,
            "stt": stt,
            "exchange_charges": exchange_charges,
            "sebi_charges": sebi_charges,
            "gst": gst,
            "stamp_duty": stamp_duty,
            "slippage_estimate": slippage,
            "total_charges": total_taxes_and_charges
        }

    @staticmethod
    def validate_new_trade(
        capital: float,
        current_daily_loss: float,
        max_daily_loss: float,
        open_positions_count: int,
        max_open_trades: int,
        trading_halted: bool
    ) -> Tuple[bool, str]:
        """Verify circuit breaker and portfolio limits before allowing trade entry."""
        if trading_halted:
            return False, "Trading is halted for the day due to manual or circuit breaker intervention."
            
        if current_daily_loss >= max_daily_loss:
            return False, f"CIRCUIT BREAKER: Daily loss limit (₹{max_daily_loss:,.2f}) has been breached. System is halted."
            
        if open_positions_count >= max_open_trades:
            return False, f"Maximum simultaneous positions limit ({max_open_trades}) reached. Close an active position first."
            
        return True, "Trade risk validation passed."
