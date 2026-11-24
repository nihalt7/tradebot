import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any
from app.services.market_data import market_data_service, DEFAULT_NSE_SYMBOLS, IST
from app.services.technical_analysis import technical_analysis_service
from app.services.opportunity_engine import opportunity_engine

logger = logging.getLogger("tradebot.scanner")

class ScannerService:
    def __init__(self):
        self._top_buy: List[Dict[str, Any]] = []
        self._top_sell: List[Dict[str, Any]] = []
        self._active_opportunities: List[Dict[str, Any]] = []
        self._breakouts: List[Dict[str, Any]] = []
        self._breakdowns: List[Dict[str, Any]] = []
        self._unusual_volume: List[Dict[str, Any]] = []
        self._momentum_stocks: List[Dict[str, Any]] = []
        self._trend_reversals: List[Dict[str, Any]] = []
        self._last_scan_time: str = "Not scanned yet"
        self._is_scanning: bool = False

    async def scan_market(self, universe: List[str] = None) -> Dict[str, Any]:
        if self._is_scanning:
            return self.get_latest_scan_results()
            
        self._is_scanning = True
        logger.info("Starting automatic NSE market scan...")
        
        symbols_to_scan = universe or DEFAULT_NSE_SYMBOLS
        all_signals = []
        breakouts = []
        breakdowns = []
        unusual_volume = []
        momentum = []
        reversals = []

        try:
            for sym in symbols_to_scan:
                clean_sym = sym.replace(".NS", "")
                
                # Fetch multi-timeframe genuine candles (5m for trigger, 15m for confirmation)
                df_5m = await market_data_service.get_historical_candles(sym, timeframe="5m")
                df_15m = await market_data_service.get_historical_candles(sym, timeframe="15m")
                
                if df_5m is None or df_15m is None or len(df_5m) < 20:
                    continue
                    
                ind_5m = technical_analysis_service.analyze_dataframe(df_5m)
                ind_15m = technical_analysis_service.analyze_dataframe(df_15m)
                
                if not ind_5m or not ind_15m:
                    continue
                    
                # Breakout detection
                if ind_5m.get("breakout"):
                    breakouts.append({
                        "symbol": clean_sym,
                        "price": ind_5m["price"],
                        "volume_ratio": ind_5m["volume_ratio"],
                        "rsi": ind_5m["rsi"],
                        "type": "Bullish Breakout"
                    })
                    
                if ind_5m.get("breakdown"):
                    breakdowns.append({
                        "symbol": clean_sym,
                        "price": ind_5m["price"],
                        "volume_ratio": ind_5m["volume_ratio"],
                        "rsi": ind_5m["rsi"],
                        "type": "Bearish Breakdown"
                    })
                    
                # Unusual Volume (> 1.8x MA)
                if ind_5m.get("volume_ratio", 0) >= 1.8:
                    unusual_volume.append({
                        "symbol": clean_sym,
                        "price": ind_5m["price"],
                        "volume_ratio": ind_5m["volume_ratio"],
                        "type": "Volume Surge"
                    })
                    
                # Strong Momentum (ADX > 25 with RSI > 60 or < 40)
                if ind_5m.get("adx", 0) > 25:
                    if ind_5m.get("rsi", 50) > 60:
                        momentum.append({"symbol": clean_sym, "trend": "Bullish", "rsi": ind_5m["rsi"], "adx": ind_5m["adx"]})
                    elif ind_5m.get("rsi", 50) < 40:
                        momentum.append({"symbol": clean_sym, "trend": "Bearish", "rsi": ind_5m["rsi"], "adx": ind_5m["adx"]})
                        
                # Trend Reversals (Supertrend change or pattern like Hammer/Shooting Star)
                if ind_5m.get("pattern_bullish") or ind_5m.get("pattern_bearish"):
                    reversals.append({
                        "symbol": clean_sym,
                        "pattern": ind_5m.get("pattern"),
                        "direction": "Bullish" if ind_5m.get("pattern_bullish") else "Bearish"
                    })
                    
                # Generate Opportunity
                opp = opportunity_engine.generate_opportunity(
                    symbol=clean_sym,
                    indicators_primary=ind_5m,
                    indicators_higher=ind_15m,
                    timeframe="5m"
                )
                
                if opp:
                    all_signals.append(opp)
                    
            # Separate BUY and SELL and rank by setup score descending
            buy_signals = [s for s in all_signals if s["signal"] == "BUY"]
            sell_signals = [s for s in all_signals if s["signal"] == "SELL"]
            
            buy_signals.sort(key=lambda x: x["setup_score"], reverse=True)
            sell_signals.sort(key=lambda x: x["setup_score"], reverse=True)
            
            self._top_buy = buy_signals[:5]
            self._top_sell = sell_signals[:5]
            self._active_opportunities = (buy_signals + sell_signals)
            self._active_opportunities.sort(key=lambda x: x["setup_score"], reverse=True)
            self._breakouts = breakouts[:10]
            self._breakdowns = breakdowns[:10]
            self._unusual_volume = unusual_volume[:10]
            self._momentum_stocks = momentum[:10]
            self._trend_reversals = reversals[:10]
            
            self._last_scan_time = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S IST")
            logger.info(f"Scan complete: Found {len(self._top_buy)} BUY, {len(self._top_sell)} SELL opportunities.")
        except Exception as e:
            logger.error(f"Error during scan: {e}")
        finally:
            self._is_scanning = False
            
        return self.get_latest_scan_results()

    def get_latest_scan_results(self) -> Dict[str, Any]:
        return {
            "last_scan_time": self._last_scan_time,
            "is_scanning": self._is_scanning,
            "top_buy": self._top_buy,
            "top_sell": self._top_sell,
            "active_opportunities": self._active_opportunities,
            "breakouts": self._breakouts,
            "breakdowns": self._breakdowns,
            "unusual_volume": self._unusual_volume,
            "momentum": self._momentum_stocks,
            "reversals": self._trend_reversals
        }

scanner_service = ScannerService()
