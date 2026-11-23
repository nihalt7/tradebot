import math
from datetime import datetime, timedelta
from typing import Dict, Any, List
import pandas as pd
import numpy as np
from backend.app.market_data.provider_base import MarketDataProvider
from backend.app.engines.technical_indicators import TechnicalIndicatorsEngine
from backend.app.engines.risk_manager import RiskManager

class BacktestEngine:
    def __init__(self, provider: MarketDataProvider):
        self.provider = provider

    def run_backtest(
        self,
        symbol: str,
        timeframe: str = "5m",
        bars_count: int = 150,
        initial_capital: float = 500000.0,
        risk_pct: float = 1.0
    ) -> Dict[str, Any]:
        """
        Run historical simulation of the Multi-Indicator Intraday Strategy on symbol.
        Strictly prevents look-ahead bias by evaluating signals only on closed bars,
        and accounts for slippage and Indian statutory tax/brokerage charges.
        """
        df = self.provider.get_historical_ohlcv(symbol, timeframe=timeframe, limit=bars_count)
        if len(df) < 35:
            # Generate sufficient bars if needed
            from backend.app.market_data.simulator import MarketSimulator
            df = MarketSimulator()._generate_synthetic_bars(1500.0, count=bars_count, interval_minutes=5)

        # Compute indicators
        df['rsi'] = TechnicalIndicatorsEngine.calculate_rsi(df['close'], period=14)
        df['ema_9'] = TechnicalIndicatorsEngine.calculate_ema(df['close'], span=9)
        df['ema_20'] = TechnicalIndicatorsEngine.calculate_ema(df['close'], span=20)
        df['ema_50'] = TechnicalIndicatorsEngine.calculate_ema(df['close'], span=50)
        df['vwap'] = TechnicalIndicatorsEngine.calculate_vwap(df)
        df['atr'] = TechnicalIndicatorsEngine.calculate_atr(df, period=14)
        supertrend, st_dir = TechnicalIndicatorsEngine.calculate_supertrend(df, period=10, multiplier=3.0)
        df['st_dir'] = st_dir

        trades: List[Dict[str, Any]] = []
        equity = initial_capital
        equity_curve: List[Dict[str, Any]] = [{"time": "Start", "equity": round(equity, 2)}]
        
        in_position = False
        pos_dir = ""
        entry_price = 0.0
        entry_idx = 0
        entry_time = None
        stop_loss = 0.0
        target_1 = 0.0
        target_2 = 0.0
        quantity = 0

        # Simulate bar by bar to eliminate look-ahead bias
        for i in range(25, len(df) - 1):
            curr_row = df.iloc[i]
            next_row = df.iloc[i + 1]  # Execution happens on next bar
            c = curr_row['close']
            vol = curr_row['volume']
            vwap = curr_row['vwap']
            rsi = curr_row['rsi']
            st = curr_row['st_dir']
            atr = curr_row['atr']
            bar_time = str(curr_row.get('timestamp', f"Bar {i}"))

            if not in_position:
                # BUY condition: Price > VWAP, Supertrend Bullish (1), RSI between 52 and 68, EMA9 > EMA20
                if c > vwap and st == 1 and 52 <= rsi <= 68 and curr_row['ema_9'] > curr_row['ema_20']:
                    in_position = True
                    pos_dir = "BUY"
                    # Slippage applied to entry: 0.05%
                    entry_price = round(next_row['open'] * 1.0005, 2)
                    entry_idx = i + 1
                    entry_time = bar_time
                    risk_amount = max(c * 0.005, atr * 1.5)
                    stop_loss = round(entry_price - risk_amount, 2)
                    target_1 = round(entry_price + (1.5 * risk_amount), 2)
                    target_2 = round(entry_price + (2.2 * risk_amount), 2)
                    quantity = RiskManager.calculate_position_size(equity, risk_pct, entry_price, stop_loss)

                # SELL condition: Price < VWAP, Supertrend Bearish (-1), RSI between 32 and 48, EMA9 < EMA20
                elif c < vwap and st == -1 and 32 <= rsi <= 48 and curr_row['ema_9'] < curr_row['ema_20']:
                    in_position = True
                    pos_dir = "SELL"
                    entry_price = round(next_row['open'] * 0.9995, 2)
                    entry_idx = i + 1
                    entry_time = bar_time
                    risk_amount = max(c * 0.005, atr * 1.5)
                    stop_loss = round(entry_price + risk_amount, 2)
                    target_1 = round(entry_price - (1.5 * risk_amount), 2)
                    target_2 = round(entry_price - (2.2 * risk_amount), 2)
                    quantity = RiskManager.calculate_position_size(equity, risk_pct, entry_price, stop_loss)

            else:
                # Check exit conditions on next bar
                high = next_row['high']
                low = next_row['low']
                exit_price = None
                exit_reason = ""

                if pos_dir == "BUY":
                    if low <= stop_loss:
                        exit_price = round(stop_loss * 0.9995, 2)  # Slippage on SL
                        exit_reason = "STOP_LOSS"
                    elif high >= target_2:
                        exit_price = target_2
                        exit_reason = "TARGET_2"
                    elif high >= target_1 and (i - entry_idx) >= 6:
                        exit_price = target_1
                        exit_reason = "TARGET_1_TRAILED"
                    elif (i - entry_idx) >= 12:  # Max holding bars expired
                        exit_price = next_row['close']
                        exit_reason = "TIME_EXPIRED"

                elif pos_dir == "SELL":
                    if high >= stop_loss:
                        exit_price = round(stop_loss * 1.0005, 2)
                        exit_reason = "STOP_LOSS"
                    elif low <= target_2:
                        exit_price = target_2
                        exit_reason = "TARGET_2"
                    elif low <= target_1 and (i - entry_idx) >= 6:
                        exit_price = target_1
                        exit_reason = "TARGET_1_TRAILED"
                    elif (i - entry_idx) >= 12:
                        exit_price = next_row['close']
                        exit_reason = "TIME_EXPIRED"

                if exit_price is not None:
                    # Calculate gross and net PnL
                    gross_pnl = (exit_price - entry_price) * quantity if pos_dir == "BUY" else (entry_price - exit_price) * quantity
                    charges_dict = RiskManager.calculate_indian_statutory_charges(pos_dir, quantity, entry_price, exit_price)
                    total_charges = charges_dict["total_charges"]
                    net_pnl = round(gross_pnl - total_charges, 2)
                    
                    equity += net_pnl
                    equity_curve.append({"time": bar_time, "equity": round(equity, 2)})

                    trades.append({
                        "trade_num": len(trades) + 1,
                        "direction": pos_dir,
                        "entry_time": entry_time,
                        "exit_time": bar_time,
                        "entry_price": entry_price,
                        "exit_price": exit_price,
                        "quantity": quantity,
                        "gross_pnl": round(gross_pnl, 2),
                        "net_pnl": net_pnl,
                        "charges": total_charges,
                        "exit_reason": exit_reason,
                        "return_pct": round((net_pnl / (entry_price * quantity)) * 100, 2)
                    })
                    
                    in_position = False

        # Calculate metrics
        total_trades = len(trades)
        winning_trades = sum(1 for t in trades if t["net_pnl"] > 0)
        losing_trades = sum(1 for t in trades if t["net_pnl"] < 0)
        win_rate = round((winning_trades / total_trades) * 100, 1) if total_trades > 0 else 0.0
        
        gross_profit = sum(t["net_pnl"] for t in trades if t["net_pnl"] > 0)
        gross_loss = abs(sum(t["net_pnl"] for t in trades if t["net_pnl"] < 0))
        profit_factor = round(gross_profit / (gross_loss + 1e-6), 2) if gross_loss > 0 else (round(gross_profit, 2) if gross_profit > 0 else 1.0)
        
        # Max drawdown
        peak = initial_capital
        max_dd = 0.0
        for pt in equity_curve:
            eq = pt["equity"]
            if eq > peak:
                peak = eq
            dd = (peak - eq) / (peak + 1e-6)
            if dd > max_dd:
                max_dd = dd

        net_profit = round(equity - initial_capital, 2)
        total_return_pct = round((net_profit / initial_capital) * 100, 2)
        total_charges = round(sum(t["charges"] for t in trades), 2)

        return {
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "start_date": str(df.iloc[0].get('timestamp', 'T0')),
            "end_date": str(df.iloc[-1].get('timestamp', 'TN')),
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": win_rate,
            "profit_factor": profit_factor,
            "max_drawdown": round(max_dd * 100, 2),
            "total_return_pct": total_return_pct,
            "net_profit": net_profit,
            "total_charges": total_charges,
            "trades": trades,
            "equity_curve": equity_curve
        }
