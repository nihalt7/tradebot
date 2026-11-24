from fastapi import APIRouter
from app.services.scanner import scanner_service

router = APIRouter(prefix="/scanner", tags=["scanner"])

@router.get("/latest")
async def get_latest_scan():
    return scanner_service.get_latest_scan_results()

@router.post("/scan")
async def trigger_scan():
    return await scanner_service.scan_market()
