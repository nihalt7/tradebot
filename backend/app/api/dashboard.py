from fastapi import APIRouter
from backend.app.market_data.nse_provider import market_provider
from backend.app.market_data.simulator import MarketSimulator
from backend.app.market_data.universe import NSE_UNIVERSE

router = APIRouter()

@router.get("/overview")
def get_dashboard_overview():
    sim = MarketSimulator()
    overview = sim.get_market_overview()
    stocks = list(sim.stocks.values())

    # Sort gainers and losers
    sorted_by_change = sorted(stocks, key=lambda x: x["change_pct"], reverse=True)
    top_gainers = sorted_by_change[:5]
    top_losers = sorted_by_change[-5:]
    top_losers.reverse()

    # Sort volume
    highest_volume = sorted(stocks, key=lambda x: x["volume"], reverse=True)[:5]

    return {
        "indices": overview["indices"],
        "market_status": overview["market_status"],
        "market_trend": overview["market_trend"],
        "advances": overview["advances"],
        "declines": overview["declines"],
        "unchanged": overview["unchanged"],
        "timestamp": overview["timestamp"],
        "top_gainers": top_gainers,
        "top_losers": top_losers,
        "highest_volume": highest_volume
    }
