from fastapi import APIRouter
from datetime import datetime
from backend.app.core.database import get_database
from backend.app.schemas.schemas import RiskSettingsUpdate, RiskSettingsResponse

router = APIRouter()

@router.get("/", response_model=RiskSettingsResponse)
def get_risk_settings():
    db = get_database()
    user = db.users.find_one({})
    user_id = user["id"] if user else 1
    
    risk = db.risk_settings.find_one({"user_id": user_id})
    if not risk:
        risk = {
            "user_id": user_id,
            "capital": 500000.0,
            "risk_per_trade_pct": 1.0,
            "max_daily_loss": 15000.0,
            "current_daily_loss": 0.0,
            "max_open_trades": 5,
            "paper_trading_enabled": True,
            "trading_halted": False,
            "updated_at": datetime.utcnow()
        }
        db.risk_settings.insert_one(risk)

    return RiskSettingsResponse(
        capital=risk.get("capital", 500000.0),
        risk_per_trade_pct=risk.get("risk_per_trade_pct", 1.0),
        max_daily_loss=risk.get("max_daily_loss", 15000.0),
        current_daily_loss=risk.get("current_daily_loss", 0.0),
        max_open_trades=risk.get("max_open_trades", 5),
        paper_trading_enabled=risk.get("paper_trading_enabled", True),
        trading_halted=risk.get("trading_halted", False)
    )

@router.put("/update", response_model=RiskSettingsResponse)
def update_risk_settings(upd: RiskSettingsUpdate):
    db = get_database()
    user = db.users.find_one({})
    user_id = user["id"] if user else 1
    
    existing = db.risk_settings.find_one({"user_id": user_id})
    new_data = {
        "capital": upd.capital,
        "risk_per_trade_pct": upd.risk_per_trade_pct,
        "max_daily_loss": upd.max_daily_loss,
        "max_open_trades": upd.max_open_trades,
        "paper_trading_enabled": upd.paper_trading_enabled,
        "updated_at": datetime.utcnow()
    }
    
    if existing and existing.get("current_daily_loss", 0) < upd.max_daily_loss:
        new_data["trading_halted"] = False

    if existing:
        db.risk_settings.update_one({"user_id": user_id}, {"$set": new_data})
    else:
        new_data["user_id"] = user_id
        new_data["current_daily_loss"] = 0.0
        new_data["trading_halted"] = False
        db.risk_settings.insert_one(new_data)

    risk = db.risk_settings.find_one({"user_id": user_id})
    return RiskSettingsResponse(
        capital=risk["capital"],
        risk_per_trade_pct=risk["risk_per_trade_pct"],
        max_daily_loss=risk["max_daily_loss"],
        current_daily_loss=risk.get("current_daily_loss", 0.0),
        max_open_trades=risk["max_open_trades"],
        paper_trading_enabled=risk["paper_trading_enabled"],
        trading_halted=risk.get("trading_halted", False)
    )

@router.post("/reset-daily-loss")
def reset_daily_loss():
    db = get_database()
    user = db.users.find_one({})
    user_id = user["id"] if user else 1
    db.risk_settings.update_one(
        {"user_id": user_id},
        {"$set": {"current_daily_loss": 0.0, "trading_halted": False}}
    )
    return {"status": "success", "message": "Daily loss counter reset and circuit breaker lifted."}
