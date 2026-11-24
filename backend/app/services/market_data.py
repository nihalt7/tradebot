import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
import yfinance as yf
import pandas as pd

logger = logging.getLogger("tradebot.market_data")

# Indian Standard Time (IST = UTC + 5:30)
IST = timezone(timedelta(hours=5, minutes=30))

# Popular NSE Equities
DEFAULT_NSE_SYMBOLS = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
    "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "KOTAKBANK.NS", "LT.NS",
    "AXISBANK.NS", "TATAMOTORS.NS", "MARUTI.NS", "SUNPHARMA.NS", "TITAN.NS",
    "BAJFINANCE.NS", "WIPRO.NS", "HCLTECH.NS", "ASIANPAINT.NS", "TATASTEEL.NS",
    "NTPC.NS", "POWERGRID.NS", "ADANIENT.NS", "COALINDIA.NS", "ONGC.NS",
    "JSWSTEEL.NS", "M&M.NS", "BAJAJFINSV.NS", "NESTLEIND.NS", "TECHM.NS"
]

INDEX_SYMBOLS = {
    "NIFTY 50": "^NSEI",
    "BANK NIFTY": "^NSEBANK",
    "SENSEX": "^BSESN"
}

class MarketDataService:
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._cache_expiry: Dict[str, datetime] = {}
        self._last_successful_update: Optional[datetime] = None
        self._data_status: str = "OFFLINE"  # LIVE, DELAYED, OFFLINE

    def get_ist_now(self) -> datetime:
        return datetime.now(IST)

    def is_market_open(self) -> Dict[str, Any]:
        now = self.get_ist_now()
        is_weekday = now.weekday() < 5  # Mon-Fri
        current_time = now.time()
        
        market_open_time = datetime.strptime("09:15:00", "%H:%M:%S").time()
        market_close_time = datetime.strptime("15:30:00", "%H:%M:%S").time()
        
        is_open = is_weekday and (market_open_time <= current_time <= market_close_time)
        status_text = "OPEN" if is_open else "CLOSED"
        
        return {
            "is_open": is_open,
            "status": status_text,
            "ist_time": now.strftime("%Y-%m-%d %H:%M:%S IST"),
            "session": "REGULAR" if is_open else "AFTER_HOURS"
        }

    async def get_indices(self) -> List[Dict[str, Any]]:
        now = self.get_ist_now()
        cache_key = "market_indices"
        
        if cache_key in self._cache and cache_key in self._cache_expiry:
            if now < self._cache_expiry[cache_key]:
                return self._cache[cache_key]
                
        results = []
        for name, ticker_symbol in INDEX_SYMBOLS.items():
            try:
                ticker = yf.Ticker(ticker_symbol)
                # fast_info or history
                hist = ticker.history(period="5d", interval="1d")
                hist = hist.dropna(subset=["Close"])
                if not hist.empty:
                    current_close = float(hist["Close"].iloc[-1])
                    prev_close = float(hist["Close"].iloc[-2]) if len(hist) > 1 else current_close
                    change = current_close - prev_close
                    p_change = (change / prev_close) * 100 if prev_close else 0.0
                    
                    results.append({
                        "symbol": name,
                        "ticker": ticker_symbol,
                        "price": round(current_close, 2),
                        "change": round(change, 2),
                        "percent_change": round(p_change, 2),
                        "high": round(float(hist["High"].dropna().iloc[-1]), 2),
                        "low": round(float(hist["Low"].dropna().iloc[-1]), 2),
                        "open": round(float(hist["Open"].dropna().iloc[-1]), 2),
                        "prev_close": round(prev_close, 2),
                        "last_updated": now.strftime("%Y-%m-%d %H:%M:%S IST")
                    })
                    self._last_successful_update = now
                    self._data_status = "LIVE" if self.is_market_open()["is_open"] else "DELAYED"
            except Exception as e:
                logger.error(f"Error fetching index {name}: {e}")
                
        if results:
            self._cache[cache_key] = results
            self._cache_expiry[cache_key] = now + timedelta(seconds=20)
            return results
            
        return self._cache.get(cache_key, [])

    async def get_stock_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        clean_symbol = symbol.strip().upper()
        if not clean_symbol.endswith(".NS") and not clean_symbol.endswith(".BO") and not clean_symbol.startswith("^"):
            clean_symbol = f"{clean_symbol}.NS"
            
        now = self.get_ist_now()
        cache_key = f"quote_{clean_symbol}"
        if cache_key in self._cache and cache_key in self._cache_expiry:
            if now < self._cache_expiry[cache_key]:
                return self._cache[cache_key]

        try:
            ticker = yf.Ticker(clean_symbol)
            hist = ticker.history(period="5d", interval="1d")
            hist = hist.dropna(subset=["Close"])
            if hist.empty:
                return None
                
            current_close = float(hist["Close"].iloc[-1])
            prev_close = float(hist["Close"].iloc[-2]) if len(hist) > 1 else current_close
            change = current_close - prev_close
            p_change = (change / prev_close) * 100 if prev_close else 0.0
            volume = int(hist["Volume"].iloc[-1]) if not pd.isna(hist["Volume"].iloc[-1]) else 0
            avg_volume = int(hist["Volume"].mean()) if len(hist) > 0 and not pd.isna(hist["Volume"].mean()) else volume

            high_val = float(hist["High"].iloc[-1]) if not pd.isna(hist["High"].iloc[-1]) else current_close
            low_val = float(hist["Low"].iloc[-1]) if not pd.isna(hist["Low"].iloc[-1]) else current_close
            open_val = float(hist["Open"].iloc[-1]) if not pd.isna(hist["Open"].iloc[-1]) else current_close

            quote_data = {
                "symbol": clean_symbol.replace(".NS", "").replace(".BO", ""),
                "full_symbol": clean_symbol,
                "exchange": "NSE" if ".NS" in clean_symbol else "BSE",
                "price": round(current_close, 2),
                "change": round(change, 2),
                "percent_change": round(p_change, 2),
                "open": round(open_val, 2),
                "high": round(high_val, 2),
                "low": round(low_val, 2),
                "prev_close": round(prev_close, 2),
                "volume": volume,
                "avg_volume": avg_volume,
                "volume_ratio": round(volume / avg_volume, 2) if avg_volume > 0 else 1.0,
                "last_updated": now.strftime("%Y-%m-%d %H:%M:%S IST")
            }
            
            self._cache[cache_key] = quote_data
            self._cache_expiry[cache_key] = now + timedelta(seconds=15)
            self._last_successful_update = now
            self._data_status = "LIVE" if self.is_market_open()["is_open"] else "DELAYED"
            return quote_data
        except Exception as e:
            logger.error(f"Error fetching quote for {clean_symbol}: {e}")
            return None

    async def get_historical_candles(self, symbol: str, timeframe: str = "5m", period: str = "5d") -> Optional[pd.DataFrame]:
        clean_symbol = symbol.strip().upper()
        if not clean_symbol.endswith(".NS") and not clean_symbol.endswith(".BO") and not clean_symbol.startswith("^"):
            clean_symbol = f"{clean_symbol}.NS"
            
        valid_intervals = {
            "1m": ("1m", "5d"),
            "5m": ("5m", "5d"),
            "15m": ("15m", "1mo"),
            "1h": ("60m", "1mo"),
            "1d": ("1d", "6mo")
        }
        
        interval, default_period = valid_intervals.get(timeframe, ("5m", "5d"))
        if period is None:
            period = default_period

        now = self.get_ist_now()
        cache_key = f"candles_{clean_symbol}_{interval}_{period}"
        if cache_key in self._cache and cache_key in self._cache_expiry:
            if now < self._cache_expiry[cache_key]:
                return self._cache[cache_key]

        try:
            ticker = yf.Ticker(clean_symbol)
            # fetch history in non-blocking executor
            loop = asyncio.get_event_loop()
            df = await loop.run_in_executor(None, lambda: ticker.history(period=period, interval=interval))
            
            if df.empty or len(df) < 5:
                return None
                
            # Clean dataframe
            df = df.reset_index()
            # Ensure correct column naming
            rename_map = {"Date": "Datetime", "index": "Datetime"}
            df = df.rename(columns=rename_map)
            
            self._cache[cache_key] = df
            self._cache_expiry[cache_key] = now + timedelta(seconds=30)
            self._last_successful_update = now
            return df
        except Exception as e:
            logger.error(f"Error fetching candles for {clean_symbol} ({timeframe}): {e}")
            return None

    async def get_market_overview(self) -> Dict[str, Any]:
        indices = await self.get_indices()
        market_status = self.is_market_open()
        
        # Sample quotes for market breadth and top movers
        quotes = []
        for sym in DEFAULT_NSE_SYMBOLS[:15]:
            q = await self.get_stock_quote(sym)
            if q:
                quotes.append(q)

        advances = sum(1 for q in quotes if q["percent_change"] > 0)
        declines = sum(1 for q in quotes if q["percent_change"] < 0)
        unchanged = len(quotes) - (advances + declines)
        
        # Sort for gainers / losers / volume
        top_gainers = sorted(quotes, key=lambda x: x["percent_change"], reverse=True)[:5]
        top_losers = sorted(quotes, key=lambda x: x["percent_change"])[:5]
        volume_shockers = sorted(quotes, key=lambda x: x["volume_ratio"], reverse=True)[:5]
        
        trend = "BULLISH" if advances > declines * 1.5 else ("BEARISH" if declines > advances * 1.5 else "SIDEWAYS / NEUTRAL")
        
        return {
            "market_status": market_status["status"],
            "is_open": market_status["is_open"],
            "current_time_ist": market_status["ist_time"],
            "data_status": self._data_status,
            "last_updated": self._last_successful_update.strftime("%Y-%m-%d %H:%M:%S IST") if self._last_successful_update else "OFFLINE",
            "indices": indices,
            "market_trend": trend,
            "advances": advances,
            "declines": declines,
            "unchanged": unchanged,
            "advance_decline_ratio": round(advances / declines, 2) if declines > 0 else float(advances),
            "top_gainers": top_gainers,
            "top_losers": top_losers,
            "volume_shockers": volume_shockers
        }

market_data_service = MarketDataService()
