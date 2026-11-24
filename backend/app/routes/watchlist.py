from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from app.services.market_data import market_data_service
from app.services.technical_analysis import technical_analysis_service

router = APIRouter(prefix="/watchlist", tags=["watchlist"])

class WatchlistAdd(BaseModel):
    symbol: str

USER_WATCHLISTS = {
    "default_user": ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "BHARTIARTL"]
}

@router.get("")
async def get_watchlist():
    symbols = USER_WATCHLISTS.get("default_user", [])
    results = []
    
    for sym in symbols:
        quote = await market_data_service.get_stock_quote(sym)
        if quote:
            # Also get quick technical status
            df = await market_data_service.get_historical_candles(sym, timeframe="15m")
            ind = technical_analysis_service.analyze_dataframe(df) if df is not None else {}
            
            results.append({
                "symbol": sym,
                "price": quote["price"],
                "change": quote["change"],
                "percent_change": quote["percent_change"],
                "volume": quote["volume"],
                "rsi": ind.get("rsi", "N/A"),
                "vwap": ind.get("vwap", "N/A"),
                "trend": ind.get("supertrend_direction", "NEUTRAL"),
                "exchange": "NSE"
            })
        else:
            results.append({
                "symbol": sym,
                "price": 0.0,
                "change": 0.0,
                "percent_change": 0.0,
                "volume": 0,
                "rsi": "N/A",
                "vwap": "N/A",
                "trend": "NEUTRAL",
                "exchange": "NSE"
            })
            
    return {"watchlist": results, "symbols": symbols}

@router.post("")
async def add_to_watchlist(item: WatchlistAdd):
    clean_sym = item.symbol.strip().upper().replace(".NS", "").replace(".BO", "")
    current = USER_WATCHLISTS.setdefault("default_user", [])
    if clean_sym not in current:
        current.append(clean_sym)
    return {"success": True, "message": f"{clean_sym} added to watchlist", "symbols": current}

@router.delete("/{symbol}")
async def remove_from_watchlist(symbol: str):
    clean_sym = symbol.strip().upper().replace(".NS", "").replace(".BO", "")
    current = USER_WATCHLISTS.get("default_user", [])
    if clean_sym in current:
        current.remove(clean_sym)
    return {"success": True, "message": f"{clean_sym} removed from watchlist", "symbols": current}
