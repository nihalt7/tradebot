import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime
from app.services.market_data import market_data_service
from app.services.technical_analysis import technical_analysis_service
from app.services.risk_management import risk_management_service

class BacktestEngine:
    async def run_backtest(
        self,
        symbol: str = "RELIANCE",
        strategy: str = "EMA_CROSSOVER_RSI",
        timeframe: str = "15m",
        initial_capital: float = 1000000.0,
        risk_per_trade: float = 1.0,
        period: str = "1mo"
    ) -> Dict[str, Any]:
        
        # 1. Fetch genuine historical OHLCV data
        df = await market_data_service.get_historical_candles(symbol, timeframe=timeframe, period=period)
        if df is None or len(df) < 50:
            return {
                "success": False,
                "message": f"Insufficient historical data available for {symbol} ({timeframe}). Minimum 50 candles required.",
                "data_status": "DATA UNAVAILABLE"
            }
            
        # 2. Calculate Indicators on whole series without lookahead bias
        close = df['Close']
        high = df['High']
        low = df['Low']
        volume = df['Volume']
        
        ema9 = technical_analysis_service.calculate_ema(close, 9)
        ema20 = technical_analysis_service.calculate_ema(close, 20)
        rsi = technical_analysis_service.calculate_rsi(close, 14)
        vwap = technical_analysis_service.calculate_vwap(df)
        st_data = technical_analysis_service.calculate_supertrend(df, 10, 3.0)
        atr = technical_analysis_service.calculate_atr(df, 14)
        vol_ma = technical_analysis_service.calculate_sma(volume, 20)
        
        # 3. Simulate bar-by-bar execution (Enter at open of i+1 after signal at close of i)
        capital = initial_capital
        equity_curve = [initial_capital]
        trades: List[Dict[str, Any]] = []
        
        in_position = False
        pos_side = None
        entry_price = 0.0
        stop_loss = 0.0
        target = 0.0
        pos_qty = 0
        entry_idx = 0
        
        n = len(df)
        # Train / Test split for out-of-sample verification
        split_idx = int(n * 0.7)
        
        for i in range(25, n - 1):
            curr_c = close.iloc[i]
            curr_h = high.iloc[i]
            curr_l = low.iloc[i]
            next_o = df['Open'].iloc[i+1] # realistic entry at next candle open
            curr_atr = atr.iloc[i]
            
            # Check exit if in position
            if in_position:
                hit_target = False
                hit_sl = False
                exit_price = 0.0
                exit_reason = ""
                
                if pos_side == "BUY":
                    if curr_h >= target:
                        hit_target = True
                        exit_price = target
                        exit_reason = "Target Hit"
                    elif curr_l <= stop_loss:
                        hit_sl = True
                        exit_price = stop_loss
                        exit_reason = "Stop Loss Hit"
                    elif i - entry_idx >= 30: # Max holding period reached
                        exit_price = curr_c
                        exit_reason = "Time Expiry"
                else: # SELL
                    if curr_l <= target:
                        hit_target = True
                        exit_price = target
                        exit_reason = "Target Hit"
                    elif curr_h >= stop_loss:
                        hit_sl = True
                        exit_price = stop_loss
                        exit_reason = "Stop Loss Hit"
                    elif i - entry_idx >= 30:
                        exit_price = curr_c
                        exit_reason = "Time Expiry"
                        
                if hit_target or hit_sl or (i - entry_idx >= 30) or (i == n - 2):
                    if not exit_price:
                        exit_price = curr_c
                    # Calculate PnL
                    if pos_side == "BUY":
                        gross_pnl = (exit_price - entry_price) * pos_qty
                    else:
                        gross_pnl = (entry_price - exit_price) * pos_qty
                        
                    buy_v = (entry_price if pos_side == "BUY" else exit_price) * pos_qty
                    sell_v = (exit_price if pos_side == "BUY" else entry_price) * pos_qty
                    charges = risk_management_service.estimate_indian_charges(buy_v, sell_v)["total_taxes_and_charges"]
                    net_pnl = gross_pnl - charges
                    
                    capital += net_pnl
                    equity_curve.append(capital)
                    
                    timestamp_str = str(df['Datetime'].iloc[i]) if 'Datetime' in df.columns else f"Bar {i}"
                    
                    trades.append({
                        "trade_num": len(trades) + 1,
                        "side": pos_side,
                        "entry_bar": entry_idx,
                        "exit_bar": i,
                        "entry_price": round(entry_price, 2),
                        "exit_price": round(exit_price, 2),
                        "quantity": pos_qty,
                        "gross_pnl": round(gross_pnl, 2),
                        "charges": round(charges, 2),
                        "net_pnl": round(net_pnl, 2),
                        "return_pct": round((net_pnl / (entry_price * pos_qty)) * 100, 2),
                        "exit_reason": exit_reason,
                        "timestamp": timestamp_str,
                        "sample_type": "In-Sample" if i < split_idx else "Out-Of-Sample"
                    })
                    
                    in_position = False
                    pos_side = None
                    continue
                    
            # Check entry signal if not in position
            if not in_position:
                signal_side = None
                
                if strategy == "EMA_CROSSOVER_RSI":
                    # EMA 9 crosses above EMA 20 with RSI > 50
                    if (ema9.iloc[i-1] <= ema20.iloc[i-1]) and (ema9.iloc[i] > ema20.iloc[i]) and (rsi.iloc[i] > 52):
                        signal_side = "BUY"
                    elif (ema9.iloc[i-1] >= ema20.iloc[i-1]) and (ema9.iloc[i] < ema20.iloc[i]) and (rsi.iloc[i] < 48):
                        signal_side = "SELL"
                        
                elif strategy == "SUPERTREND_BREAKOUT":
                    # Supertrend trend flip + volume surge
                    st_trend = st_data["trend"]
                    is_vol_surge = volume.iloc[i] > vol_ma.iloc[i] * 1.2
                    if st_trend.iloc[i-1] == -1 and st_trend.iloc[i] == 1 and is_vol_surge:
                        signal_side = "BUY"
                    elif st_trend.iloc[i-1] == 1 and st_trend.iloc[i] == -1 and is_vol_surge:
                        signal_side = "SELL"
                        
                elif strategy == "VWAP_PULLBACK":
                    # Price bounces off VWAP
                    vw = vwap.iloc[i]
                    if (curr_l <= vw <= curr_c) and (ema9.iloc[i] > ema20.iloc[i]):
                        signal_side = "BUY"
                    elif (curr_h >= vw >= curr_c) and (ema9.iloc[i] < ema20.iloc[i]):
                        signal_side = "SELL"
                        
                if signal_side:
                    in_position = True
                    pos_side = signal_side
                    entry_price = next_o
                    entry_idx = i + 1
                    
                    # Risk & Targets: 1.5 ATR risk, 2.5 ATR target (1:1.66 R:R)
                    risk_dist = max(curr_atr * 1.5, entry_price * 0.007)
                    if signal_side == "BUY":
                        stop_loss = entry_price - risk_dist
                        target = entry_price + (risk_dist * 2.5)
                    else:
                        stop_loss = entry_price + risk_dist
                        target = entry_price - (risk_dist * 2.5)
                        
                    # Position Sizing
                    risk_cash = capital * (risk_per_trade / 100.0)
                    pos_qty = int(risk_cash / risk_dist) if risk_dist > 0 else 1
                    pos_qty = max(1, pos_qty)

        # 4. Compute performance metrics
        total_trades = len(trades)
        if total_trades == 0:
            return {
                "success": True,
                "strategy": strategy,
                "symbol": symbol,
                "total_trades": 0,
                "message": "Strategy criteria did not trigger any trades in this period."
            }
            
        winning_trades = [t for t in trades if t["net_pnl"] > 0]
        losing_trades = [t for t in trades if t["net_pnl"] < 0]
        
        win_rate = (len(winning_trades) / total_trades) * 100
        gross_profit = sum(t["net_pnl"] for t in winning_trades)
        gross_loss = abs(sum(t["net_pnl"] for t in losing_trades))
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else (gross_profit if gross_profit > 0 else 1.0)
        
        avg_profit = (gross_profit / len(winning_trades)) if winning_trades else 0.0
        avg_loss = (gross_loss / len(losing_trades)) if losing_trades else 0.0
        
        total_pnl = sum(t["net_pnl"] for t in trades)
        total_return_pct = (total_pnl / initial_capital) * 100
        
        # Drawdown calculation
        equity_series = pd.Series(equity_curve)
        peak = equity_series.cummax()
        drawdown = (equity_series - peak) / peak * 100
        max_drawdown = abs(drawdown.min())
        
        # Out of sample breakdown
        in_sample_trades = [t for t in trades if t["sample_type"] == "In-Sample"]
        out_sample_trades = [t for t in trades if t["sample_type"] == "Out-Of-Sample"]
        
        in_win_rate = (len([t for t in in_sample_trades if t['net_pnl'] > 0]) / len(in_sample_trades) * 100) if in_sample_trades else 0
        out_win_rate = (len([t for t in out_sample_trades if t['net_pnl'] > 0]) / len(out_sample_trades) * 100) if out_sample_trades else 0
        
        return {
            "success": True,
            "strategy": strategy,
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "initial_capital": initial_capital,
            "ending_capital": round(capital, 2),
            "total_net_pnl": round(total_pnl, 2),
            "total_return_percent": round(total_return_pct, 2),
            "total_trades": total_trades,
            "win_rate": round(win_rate, 2),
            "profit_factor": round(profit_factor, 2),
            "max_drawdown_percent": round(max_drawdown, 2),
            "average_win": round(avg_profit, 2),
            "average_loss": round(avg_loss, 2),
            "risk_reward_realized": round(avg_profit / avg_loss, 2) if avg_loss > 0 else 0.0,
            "in_sample_win_rate": round(in_win_rate, 2),
            "out_of_sample_win_rate": round(out_win_rate, 2),
            "equity_curve": [round(x, 2) for x in equity_curve[-40:]], # sample points for charting
            "recent_trades": trades[-15:]
        }

backtest_engine = BacktestEngine()
