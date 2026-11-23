from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from backend.app.core.database import get_database
from backend.app.schemas.schemas import PaperOrderRequest, ActivePositionResponse
from backend.app.engines.risk_manager import RiskManager
from backend.app.market_data.nse_provider import market_provider

router = APIRouter()

@router.get("/active")
def get_active_signals():
    db = get_database()
    signals = db.trading_signals.find({"status": "ACTIVE"}, sort=[("generated_at", -1)], limit=20)
    
    if not signals:
        from backend.app.api.scanner import scanner_engine
        results = scanner_engine.cached_results
        if not results.get("top_buys"):
            results = scanner_engine.run_market_scan()
        
        for b in results.get("top_buys", [])[:3]:
            sig_id = f"SIG_{b['symbol']}_{int(datetime.now().timestamp())}"
            sig_doc = {
                "id": sig_id,
                "symbol": b["symbol"],
                "exchange": "NSE",
                "signal_type": "BUY",
                "source_engine": "SCANNER",
                "entry_min": b["entry_min"],
                "entry_max": b["entry_max"],
                "stop_loss": b["stop_loss"],
                "target_1": b["target_1"],
                "target_2": b["target_2"],
                "target_3": b["target_3"],
                "risk_reward": b["risk_reward"],
                "setup_score": b["score"],
                "timeframe": "5m",
                "status": "ACTIVE",
                "generated_at": datetime.utcnow(),
                "expires_at": datetime.utcnow(),
                "reason": b["reason"]
            }
            db.trading_signals.insert_one(sig_doc)
        signals = db.trading_signals.find({"status": "ACTIVE"})

    return signals

@router.get("/positions", response_model=List[ActivePositionResponse])
def get_active_positions():
    db = get_database()
    user = db.users.find_one({})
    user_id = user["id"] if user else 1
    
    positions = db.active_positions.find({"user_id": user_id, "status": "OPEN"})
    res = []
    for pos in positions:
        q = market_provider.get_quote(pos["symbol"])
        curr_p = q.get("price", pos["entry_price"])
        
        diff = curr_p - pos["entry_price"] if pos["direction"] == "BUY" else pos["entry_price"] - curr_p
        pnl = round(diff * pos["quantity"], 2)
        pnl_pct = round((diff / pos["entry_price"]) * 100, 2)

        # Update in Mongo
        db.active_positions.update_one(
            {"id": pos["id"]},
            {"$set": {"current_price": curr_p, "pnl": pnl, "pnl_percentage": pnl_pct}}
        )

        pos["current_price"] = curr_p
        pos["pnl"] = pnl
        pos["pnl_percentage"] = pnl_pct
        if not isinstance(pos.get("opened_at"), datetime):
            pos["opened_at"] = datetime.utcnow()
        res.append(ActivePositionResponse.model_validate(pos))

    return res

@router.post("/paper-order")
def place_paper_order(order: PaperOrderRequest):
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
            "trading_halted": False
        }
        db.risk_settings.insert_one(risk)

    open_count = db.active_positions.count_documents({"user_id": user_id, "status": "OPEN"})
    
    # Risk check
    allowed, reason = RiskManager.validate_new_trade(
        capital=risk["capital"],
        current_daily_loss=risk.get("current_daily_loss", 0.0),
        max_daily_loss=risk["max_daily_loss"],
        open_positions_count=open_count,
        max_open_trades=risk["max_open_trades"],
        trading_halted=risk.get("trading_halted", False)
    )
    if not allowed:
        raise HTTPException(status_code=400, detail=reason)

    pos_count = db.active_positions.count_documents({})
    pos_id = pos_count + 1

    pos_doc = {
        "id": pos_id,
        "user_id": user_id,
        "signal_id": order.signal_id,
        "symbol": order.symbol.upper(),
        "direction": order.direction.upper(),
        "quantity": order.quantity,
        "entry_price": order.entry_price,
        "current_price": order.entry_price,
        "stop_loss": order.stop_loss,
        "target_1": order.target_1,
        "target_2": order.target_2,
        "target_3": order.target_3,
        "pnl": 0.0,
        "pnl_percentage": 0.0,
        "mode": "PAPER",
        "status": "OPEN",
        "opened_at": datetime.utcnow()
    }
    db.active_positions.insert_one(pos_doc)

    return {"status": "success", "message": f"Paper Trade executed for {order.quantity} shares of {order.symbol}", "position_id": pos_id}

@router.post("/positions/{position_id}/close")
def close_position(position_id: int):
    db = get_database()
    user = db.users.find_one({})
    user_id = user["id"] if user else 1

    pos = db.active_positions.find_one({"id": position_id, "user_id": user_id})
    if not pos:
        raise HTTPException(status_code=404, detail="Position not found")

    q = market_provider.get_quote(pos["symbol"])
    exit_price = q.get("price", pos["current_price"])

    gross_diff = exit_price - pos["entry_price"] if pos["direction"] == "BUY" else pos["entry_price"] - exit_price
    gross_pnl = round(gross_diff * pos["quantity"], 2)

    charges = RiskManager.calculate_indian_statutory_charges(pos["direction"], pos["quantity"], pos["entry_price"], exit_price)
    net_pnl = round(gross_pnl - charges["total_charges"], 2)

    closed_at = datetime.utcnow()

    # Update position status in MongoDB
    db.active_positions.update_one(
        {"id": position_id},
        {"$set": {"status": "CLOSED", "closed_at": closed_at, "current_price": exit_price}}
    )

    # Log in Trading History
    hist_count = db.trading_history.count_documents({})
    db.trading_history.insert_one({
        "id": hist_count + 1,
        "user_id": user_id,
        "symbol": pos["symbol"],
        "direction": pos["direction"],
        "quantity": pos["quantity"],
        "entry_price": pos["entry_price"],
        "exit_price": exit_price,
        "entry_time": pos["opened_at"],
        "exit_time": closed_at,
        "gross_pnl": gross_pnl,
        "net_pnl": net_pnl,
        "charges": charges["total_charges"],
        "exit_reason": "MANUAL_SQUARE_OFF"
    })

    # Update circuit breaker if loss
    if net_pnl < 0:
        db.risk_settings.update_one(
            {"user_id": user_id},
            {"$inc": {"current_daily_loss": abs(net_pnl)}}
        )
        risk = db.risk_settings.find_one({"user_id": user_id})
        if risk and risk.get("current_daily_loss", 0) >= risk.get("max_daily_loss", 15000):
            db.risk_settings.update_one({"user_id": user_id}, {"$set": {"trading_halted": True}})

    return {
        "status": "success",
        "symbol": pos["symbol"],
        "net_pnl": net_pnl,
        "gross_pnl": gross_pnl,
        "charges": charges["total_charges"]
    }
