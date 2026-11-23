from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
from backend.app.core.database import get_database
from backend.app.schemas.schemas import WatchlistAddRequest, WatchlistItem
from backend.app.market_data.nse_provider import market_provider

router = APIRouter()

@router.get("/", response_model=List[WatchlistItem])
def get_watchlist():
    db = get_database()
    user = db.users.find_one({})
    user_id = user["id"] if user else 1
    items = db.watchlists.find({"user_id": user_id})
    
    if not items:
        defaults = ["RELIANCE", "TCS", "HDFCBANK", "INFY"]
        for idx, s in enumerate(defaults):
            w = {
                "id": idx + 1,
                "user_id": user_id,
                "symbol": s,
                "exchange": "NSE",
                "notes": "Core bluechip",
                "added_at": datetime.utcnow()
            }
            db.watchlists.insert_one(w)
        items = db.watchlists.find({"user_id": user_id})

    result: List[WatchlistItem] = []
    for w in items:
        sym = w["symbol"]
        q = market_provider.get_quote(sym)
        result.append(WatchlistItem(
            id=w.get("id", 1),
            symbol=sym,
            exchange=w.get("exchange", "NSE"),
            company_name=q.get("name", sym),
            sector=q.get("sector", "Equity"),
            current_price=q.get("price", 0.0),
            change_pct=q.get("change_pct", 0.0),
            high=q.get("high", 0.0),
            low=q.get("low", 0.0),
            volume=q.get("volume", 0.0),
            vwap=q.get("vwap", 0.0),
            trend=q.get("trend", "Neutral"),
            added_at=w.get("added_at") if isinstance(w.get("added_at"), datetime) else datetime.utcnow()
        ))
    return result

@router.post("/add")
def add_to_watchlist(req: WatchlistAddRequest):
    db = get_database()
    user = db.users.find_one({})
    user_id = user["id"] if user else 1
    sym = req.symbol.upper().replace(".NS", "").strip()
    
    existing = db.watchlists.find_one({"user_id": user_id, "symbol": sym})
    if existing:
        return {"status": "exists", "message": f"{sym} is already in your watchlist."}

    count = db.watchlists.count_documents({})
    item = {
        "id": count + 1,
        "user_id": user_id,
        "symbol": sym,
        "exchange": "NSE",
        "notes": req.notes,
        "added_at": datetime.utcnow()
    }
    db.watchlists.insert_one(item)
    
    quote = market_provider.get_quote(sym)
    return {"status": "success", "symbol": sym, "price": quote.get("price", 0.0)}

@router.delete("/remove/{symbol}")
def remove_from_watchlist(symbol: str):
    db = get_database()
    user = db.users.find_one({})
    user_id = user["id"] if user else 1
    sym = symbol.upper().replace(".NS", "").strip()

    existing = db.watchlists.find_one({"user_id": user_id, "symbol": sym})
    if not existing:
        raise HTTPException(status_code=404, detail="Stock not found in watchlist")

    db.watchlists.delete_one({"user_id": user_id, "symbol": sym})
    return {"status": "success", "message": f"Removed {sym} from watchlist"}
