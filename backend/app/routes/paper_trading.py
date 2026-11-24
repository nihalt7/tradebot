from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.paper_trading import paper_trading_service
from app.services.market_data import market_data_service

router = APIRouter(prefix="/paper-trading", tags=["paper-trading"])

class OrderRequest(BaseModel):
    symbol: str
    side: str  # BUY or SELL
    quantity: int
    price: float
    stop_loss: Optional[float] = None
    target: Optional[float] = None
    signal_id: Optional[str] = None

class CloseRequest(BaseModel):
    exit_price: Optional[float] = None
    reason: Optional[str] = "Manual Close"

@router.get("/portfolio")
async def get_portfolio():
    # Gather live prices for open positions
    live_prices = {}
    for pos_id, pos in paper_trading_service.open_positions.items():
        sym = pos["symbol"]
        quote = await market_data_service.get_stock_quote(sym)
        if quote:
            live_prices[sym] = quote["price"]
            
    return paper_trading_service.get_portfolio_summary(live_prices)

@router.post("/order")
async def place_order(order: OrderRequest):
    result = paper_trading_service.execute_order(
        symbol=order.symbol,
        side=order.side,
        quantity=order.quantity,
        price=order.price,
        stop_loss=order.stop_loss,
        target=order.target,
        signal_id=order.signal_id
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.post("/close/{pos_id}")
async def close_position(pos_id: str, req: CloseRequest):
    pos = paper_trading_service.open_positions.get(pos_id)
    if not pos:
        raise HTTPException(status_code=404, detail="Position not found")
        
    exit_price = req.exit_price
    if not exit_price:
        quote = await market_data_service.get_stock_quote(pos["symbol"])
        exit_price = quote["price"] if quote else pos["entry_price"]
        
    result = paper_trading_service.close_position(pos_id, exit_price, reason=req.reason)
    return result
