from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.services.backtesting import backtest_engine

router = APIRouter(prefix="/backtesting", tags=["backtesting"])

class BacktestRequest(BaseModel):
    symbol: str = "RELIANCE"
    strategy: str = "EMA_CROSSOVER_RSI" # EMA_CROSSOVER_RSI, SUPERTREND_BREAKOUT, VWAP_PULLBACK
    timeframe: str = "15m"
    initial_capital: float = 1000000.0
    risk_per_trade: float = 1.0
    period: str = "1mo"

@router.post("/run")
async def run_backtest(req: BacktestRequest):
    return await backtest_engine.run_backtest(
        symbol=req.symbol,
        strategy=req.strategy,
        timeframe=req.timeframe,
        initial_capital=req.initial_capital,
        risk_per_trade=req.risk_per_trade,
        period=req.period
    )
