from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from app.services.market_data import market_data_service, DEFAULT_NSE_SYMBOLS

router = APIRouter(prefix="/market", tags=["market"])

@router.get("/overview")
async def get_overview():
    return await market_data_service.get_market_overview()

@router.get("/indices")
async def get_indices():
    return await market_data_service.get_indices()

@router.get("/status")
async def get_market_status():
    return market_data_service.is_market_open()

@router.get("/quote/{symbol}")
async def get_quote(symbol: str):
    quote = await market_data_service.get_stock_quote(symbol)
    if not quote:
        raise HTTPException(status_code=404, detail=f"Stock quote not found for {symbol}")
    return quote

@router.get("/history/{symbol}")
async def get_history(symbol: str, timeframe: str = "5m", period: Optional[str] = "5d"):
    df = await market_data_service.get_historical_candles(symbol, timeframe=timeframe, period=period)
    if df is None or df.empty:
        raise HTTPException(status_code=404, detail=f"Historical data not found for {symbol}")
        
    records = []
    for _, row in df.iterrows():
        dt = row.get("Datetime", row.get("Date"))
        records.append({
            "time": str(dt),
            "open": round(float(row["Open"]), 2),
            "high": round(float(row["High"]), 2),
            "low": round(float(row["Low"]), 2),
            "close": round(float(row["Close"]), 2),
            "volume": int(row["Volume"])
        })
    return {"symbol": symbol, "timeframe": timeframe, "candles": records}
