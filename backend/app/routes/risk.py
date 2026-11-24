from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.services.risk_management import risk_management_service

router = APIRouter(prefix="/risk", tags=["risk"])

class RiskSettingsUpdate(BaseModel):
    initial_capital: Optional[float] = None
    risk_per_trade_percent: Optional[float] = None
    max_daily_loss: Optional[float] = None
    max_trades_per_day: Optional[int] = None
    max_simultaneous_positions: Optional[int] = None

class PositionSizeQuery(BaseModel):
    entry_price: float
    stop_loss: float
    capital: Optional[float] = None
    risk_percent: Optional[float] = None

@router.get("/settings")
async def get_risk_settings():
    return risk_management_service.get_settings()

@router.post("/settings")
async def update_risk_settings(settings: RiskSettingsUpdate):
    updates = {k: v for k, v in settings.model_dump().items() if v is not None}
    return risk_management_service.update_settings(updates)

@router.post("/calculate-position")
async def calculate_position(query: PositionSizeQuery):
    return risk_management_service.calculate_position_size(
        entry_price=query.entry_price,
        stop_loss=query.stop_loss,
        capital=query.capital,
        risk_percent=query.risk_percent
    )
