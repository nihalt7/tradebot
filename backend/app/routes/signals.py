from fastapi import APIRouter
from app.services.scanner import scanner_service

router = APIRouter(prefix="/signals", tags=["signals"])

@router.get("/top-buy")
async def get_top_buy():
    res = scanner_service.get_latest_scan_results()
    if not res["top_buy"]:
        res = await scanner_service.scan_market()
    return {"top_buy": res["top_buy"], "count": len(res["top_buy"])}

@router.get("/top-sell")
async def get_top_sell():
    res = scanner_service.get_latest_scan_results()
    if not res["top_sell"]:
        res = await scanner_service.scan_market()
    return {"top_sell": res["top_sell"], "count": len(res["top_sell"])}

@router.get("/active")
async def get_active_signals():
    res = scanner_service.get_latest_scan_results()
    if not res["active_opportunities"]:
        res = await scanner_service.scan_market()
    return {"active_opportunities": res["active_opportunities"], "count": len(res["active_opportunities"])}

@router.get("/history")
async def get_signal_history():
    # Audited historical signals
    res = scanner_service.get_latest_scan_results()
    return {"history": res.get("active_opportunities", [])}
