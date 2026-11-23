import json
import logging
from typing import Dict, List, Set, Any
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # Map of active websockets
        self.active_connections: Set[WebSocket] = set()
        # Map of user_id -> set of WebSockets
        self.user_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int = 1):
        await websocket.accept()
        self.active_connections.add(websocket)
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(websocket)
        logger.info(f"WebSocket client connected for user {user_id}. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket, user_id: int = 1):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if user_id in self.user_connections and websocket in self.user_connections[user_id]:
            self.user_connections[user_id].remove(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        logger.info(f"WebSocket client disconnected for user {user_id}. Remaining: {len(self.active_connections)}")

    async def broadcast_market_tick(self, data: Dict[str, Any]):
        """Broadcast live price ticks & index updates to all active clients."""
        if not self.active_connections:
            return
        payload = json.dumps({"type": "MARKET_TICK", "data": data})
        for ws in list(self.active_connections):
            try:
                await ws.send_text(payload)
            except Exception:
                self.active_connections.discard(ws)

    async def broadcast_signal_alert(self, signal_card: Dict[str, Any]):
        """Broadcast high-quality confirmed opportunity card to all clients."""
        if not self.active_connections:
            return
        payload = json.dumps({"type": "SIGNAL_ALERT", "data": signal_card})
        for ws in list(self.active_connections):
            try:
                await ws.send_text(payload)
            except Exception:
                self.active_connections.discard(ws)

    async def send_user_message(self, user_id: int, message_payload: Dict[str, Any]):
        """Send message or notification to a specific user's connected clients."""
        if user_id not in self.user_connections:
            return
        payload = json.dumps({"type": "CHAT_MESSAGE", "data": message_payload})
        for ws in list(self.user_connections[user_id]):
            try:
                await ws.send_text(payload)
            except Exception:
                pass

ws_manager = ConnectionManager()
