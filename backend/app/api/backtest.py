from fastapi import APIRouter
from backend.app.schemas.schemas import BacktestRequest, BacktestResponse
from backend.app.engines.backtest_engine import BacktestEngine
from backend.app.market_data.nse_provider import market_provider

router = APIRouter()
backtest_engine = BacktestEngine(market_provider)

@router.post("/run", response_model=BacktestResponse)
def execute_backtest(req: BacktestRequest):
    result = backtest_engine.run_backtest(
        symbol=req.symbol,
        timeframe=req.timeframe,
        bars_count=160,
        initial_capital=req.capital,
        risk_pct=req.risk_pct
    )
    return BacktestResponse(**result)
