from fastapi import APIRouter
from backend.app.schemas.schemas import ScannerResultsResponse
from backend.app.engines.scanner_engine import ScannerEngine
from backend.app.market_data.nse_provider import market_provider

router = APIRouter()
scanner_engine = ScannerEngine(market_provider)

@router.get("/latest")
def get_latest_scan_results():
    results = scanner_engine.cached_results
    if not results.get("top_buys") and not results.get("top_sells"):
        results = scanner_engine.run_market_scan()
    return results

@router.post("/scan-now")
def trigger_manual_scan():
    results = scanner_engine.run_market_scan()
    return results
