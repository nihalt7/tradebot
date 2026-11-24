import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from app.services.market_data import IST

logger = logging.getLogger("tradebot.notifications")

class NotificationService:
    def __init__(self):
        self._notifications: List[Dict[str, Any]] = []
        self._sent_signal_ids: set = set()

    def get_notifications(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._notifications[-limit:]

    def add_notification(
        self,
        title: str,
        message: str,
        notif_type: str = "INFO", # BUY_ALERT, SELL_ALERT, TARGET_HIT, SL_HIT, MARKET_UPDATE, SYSTEM
        symbol: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        
        # Check duplicate signal prevention
        if data and "signal_id" in data:
            sig_id = data["signal_id"]
            if sig_id in self._sent_signal_ids:
                return None
            self._sent_signal_ids.add(sig_id)

        now = datetime.now(IST)
        notif = {
            "id": f"notif_{int(now.timestamp() * 1000)}",
            "title": title,
            "message": message,
            "type": notif_type,
            "symbol": symbol,
            "data": data or {},
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S IST"),
            "read": False
        }
        
        self._notifications.append(notif)
        # Cap notifications list
        if len(self._notifications) > 200:
            self._notifications = self._notifications[-200:]
            
        logger.info(f"Notification added: [{notif_type}] {title}")
        return notif

    def mark_all_read(self):
        for n in self._notifications:
            n["read"] = True

notification_service = NotificationService()
