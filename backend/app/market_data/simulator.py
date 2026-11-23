import random
import time
import math
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List
import pandas as pd
import numpy as np
from backend.app.market_data.universe import NSE_UNIVERSE, NSE_INDEX_SYMBOLS

class MarketSimulator:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MarketSimulator, cls).__new__(cls)
            cls._instance._init_state()
        return cls._instance

    def _init_state(self):
        self.stocks: Dict[str, Dict[str, Any]] = {}
        self.bars: Dict[str, Dict[str, pd.DataFrame]] = {}  # symbol -> {timeframe: df}
        self.indices: Dict[str, Dict[str, Any]] = {}
        
        # Initialize indices
        for idx_name, data in NSE_INDEX_SYMBOLS.items():
            base = data["base_value"]
            self.indices[idx_name] = {
                "name": idx_name,
                "symbol": data["symbol"],
                "price": base,
                "open": base,
                "high": base * 1.006,
                "low": base * 0.994,
                "prev_close": base * 0.997,
                "change": base * 0.003,
                "change_pct": 0.30,
                "trend": "Bullish"
            }

        # Seed realistic starting price histories for universe stocks
        now = datetime.now()
        for item in NSE_UNIVERSE:
            sym = item["symbol"]
            base = item["base_price"]
            # Setup dynamic regimes: assign some stocks as momentum breakout, some rangebound, some breakdown
            h = hash(sym)
            regime = "MOMENTUM_BULL" if (h % 5 == 0) else ("MOMENTUM_BEAR" if (h % 7 == 0) else "NEUTRAL")
            
            # Generate 120 bars of 5m historical data
            df_5m = self._generate_synthetic_bars(base, count=150, interval_minutes=5, regime=regime)
            current_close = float(df_5m["close"].iloc[-1])
            open_day = float(df_5m["open"].iloc[max(0, len(df_5m) - 30)])
            high_day = float(df_5m["high"].iloc[-30:].max())
            low_day = float(df_5m["low"].iloc[-30:].min())
            vol_day = float(df_5m["volume"].iloc[-30:].sum())
            cum_pv = (df_5m["close"] * df_5m["volume"]).iloc[-30:].sum()
            vwap_day = float(cum_pv / (vol_day + 1e-6))
            prev_close = float(df_5m["close"].iloc[max(0, len(df_5m) - 31)])

            self.stocks[sym] = {
                "symbol": sym,
                "name": item["name"],
                "sector": item["sector"],
                "lot_size": item["lot_size"],
                "price": current_close,
                "open": open_day,
                "high": high_day,
                "low": low_day,
                "prev_close": prev_close,
                "volume": vol_day,
                "vwap": vwap_day,
                "change": round(current_close - prev_close, 2),
                "change_pct": round(((current_close - prev_close) / prev_close) * 100, 2),
                "trend": "Bullish" if current_close >= open_day else "Bearish",
                "regime": regime,
                "last_update": now
            }
            self.bars[sym] = {
                "5m": df_5m
            }

    def _generate_synthetic_bars(self, base_price: float, count: int = 150, interval_minutes: int = 5, regime: str = "NEUTRAL") -> pd.DataFrame:
        now = datetime.now()
        times = [now - timedelta(minutes=(count - i) * interval_minutes) for i in range(count)]
        
        prices = [base_price]
        drift = 0.0003 if regime == "MOMENTUM_BULL" else (-0.0003 if regime == "MOMENTUM_BEAR" else 0.0)
        volatility = 0.0035

        for _ in range(count - 1):
            ret = np.random.normal(drift, volatility)
            p = max(5.0, prices[-1] * (1.0 + ret))
            prices.append(round(p, 2))

        opens, highs, lows, closes, volumes, vwaps = [], [], [], [], [], []
        cum_vol = 0.0
        cum_pv = 0.0

        for i, p in enumerate(prices):
            bar_volatility = np.random.uniform(0.001, 0.004)
            o = prices[i - 1] if i > 0 else p
            c = p
            h = max(o, c) * (1.0 + abs(np.random.normal(0, bar_volatility)))
            l = min(o, c) * (1.0 - abs(np.random.normal(0, bar_volatility)))
            base_vol = 50000 + int(abs(np.random.normal(20000, 15000)))
            if regime in ("MOMENTUM_BULL", "MOMENTUM_BEAR") and i >= count - 15:
                base_vol = int(base_vol * np.random.uniform(1.8, 3.2)) # volume breakout
            
            cum_vol += base_vol
            cum_pv += ((h + l + c) / 3.0) * base_vol
            vwap = cum_pv / (cum_vol + 1e-6)

            opens.append(round(o, 2))
            highs.append(round(h, 2))
            lows.append(round(l, 2))
            closes.append(round(c, 2))
            volumes.append(base_vol)
            vwaps.append(round(vwap, 2))

        df = pd.DataFrame({
            "timestamp": times,
            "open": opens,
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": volumes,
            "vwap": vwaps
        })
        return df

    def tick(self):
        """Simulate microsecond/second ticks for live streaming price evolution."""
        for sym, stock in self.stocks.items():
            drift = 0.00015 if stock["regime"] == "MOMENTUM_BULL" else (-0.00015 if stock["regime"] == "MOMENTUM_BEAR" else 0.0)
            ret = np.random.normal(drift, 0.0008)
            new_price = round(max(5.0, stock["price"] * (1.0 + ret)), 2)
            stock["price"] = new_price
            stock["high"] = max(stock["high"], new_price)
            stock["low"] = min(stock["low"], new_price)
            added_vol = int(abs(np.random.normal(800, 400)))
            stock["volume"] += added_vol
            stock["change"] = round(new_price - stock["prev_close"], 2)
            stock["change_pct"] = round((stock["change"] / stock["prev_close"]) * 100, 2)
            stock["last_update"] = datetime.now()

            # Update the latest bar in df
            if sym in self.bars and "5m" in self.bars[sym]:
                df = self.bars[sym]["5m"]
                last_idx = len(df) - 1
                df.at[last_idx, "close"] = new_price
                df.at[last_idx, "high"] = max(df.at[last_idx, "high"], new_price)
                df.at[last_idx, "low"] = min(df.at[last_idx, "low"], new_price)
                df.at[last_idx, "volume"] = df.at[last_idx, "volume"] + added_vol

        # Update indices
        for idx_name, idx_data in self.indices.items():
            ret = np.random.normal(0.00005, 0.0003)
            p = round(idx_data["price"] * (1.0 + ret), 2)
            idx_data["price"] = p
            idx_data["high"] = max(idx_data["high"], p)
            idx_data["low"] = min(idx_data["low"], p)
            idx_data["change"] = round(p - idx_data["prev_close"], 2)
            idx_data["change_pct"] = round((idx_data["change"] / idx_data["prev_close"]) * 100, 2)
            idx_data["trend"] = "Bullish" if idx_data["change"] >= 0 else "Bearish"

    def get_quote(self, symbol: str) -> Dict[str, Any]:
        sym = symbol.upper().replace(".NS", "")
        if sym in self.stocks:
            return self.stocks[sym]
        # Return fallback base if not present
        return {
            "symbol": sym,
            "name": sym,
            "sector": "Equity",
            "lot_size": 1,
            "price": 1000.0,
            "open": 995.0,
            "high": 1010.0,
            "low": 990.0,
            "prev_close": 992.0,
            "volume": 250000,
            "vwap": 1002.50,
            "change": 8.0,
            "change_pct": 0.81,
            "trend": "Bullish",
            "last_update": datetime.now()
        }

    def get_historical_ohlcv(self, symbol: str, timeframe: str = "5m", limit: int = 100) -> pd.DataFrame:
        sym = symbol.upper().replace(".NS", "")
        if sym in self.bars and "5m" in self.bars[sym]:
            df = self.bars[sym]["5m"].copy()
            if timeframe == "15m":
                # Resample 5m to 15m
                df.set_index("timestamp", inplace=True)
                df_resampled = df.resample("15min").agg({
                    "open": "first",
                    "high": "max",
                    "low": "min",
                    "close": "last",
                    "volume": "sum",
                    "vwap": "last"
                }).dropna().reset_index()
                return df_resampled.tail(limit)
            elif timeframe == "1h":
                df.set_index("timestamp", inplace=True)
                df_resampled = df.resample("60min").agg({
                    "open": "first",
                    "high": "max",
                    "low": "min",
                    "close": "last",
                    "volume": "sum",
                    "vwap": "last"
                }).dropna().reset_index()
                return df_resampled.tail(limit)
            return df.tail(limit)
        
        # If not cached, generate on the fly
        base = 1000.0
        return self._generate_synthetic_bars(base, count=limit, interval_minutes=5)

    def get_market_overview(self) -> Dict[str, Any]:
        adv = sum(1 for s in self.stocks.values() if s["change"] > 0)
        dec = sum(1 for s in self.stocks.values() if s["change"] < 0)
        neutral = len(self.stocks) - adv - dec
        nifty = self.indices["NIFTY 50"]
        overall_trend = "Bullish" if nifty["change_pct"] > 0.15 else ("Bearish" if nifty["change_pct"] < -0.15 else "Sideways")

        return {
            "indices": self.indices,
            "market_status": "OPEN" if self.is_market_open() else "PRE_MARKET / SIMULATED",
            "market_trend": overall_trend,
            "advances": adv,
            "declines": dec,
            "unchanged": neutral,
            "timestamp": datetime.now().strftime("%I:%M:%S %p IST")
        }

    def is_market_open(self) -> bool:
        now = datetime.now()
        # Monday = 0, Friday = 4
        if now.weekday() >= 5:
            return False
        # 09:15 to 15:30
        market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
        market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
        return market_open <= now <= market_close
