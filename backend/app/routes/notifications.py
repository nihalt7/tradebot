from fastapi import APIRouter
from app.services.notifications import notification_service

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("")
async def get_notifications():
    return {"notifications": notification_service.get_notifications()}

@router.post("/mark-read")
async def mark_notifications_read():
    notification_service.mark_all_read()
    return {"success": True}
