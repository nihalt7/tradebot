import logging
from typing import List, Dict, Any
from fastapi import WebSocket

logger = logging.getLogger("tradebot.websocket")

class WebSocketManager:
    def __init__(self):
        self.market_connections: List[WebSocket] = []
        self.chat_connections: List[WebSocket] = []
        self.notification_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket, channel: str = "market"):
        await websocket.accept()
        if channel == "market":
            self.market_connections.append(websocket)
        elif channel == "chat":
            self.chat_connections.append(websocket)
        elif channel == "notifications":
            self.notification_connections.append(websocket)
        logger.info(f"WebSocket client connected to channel '{channel}'. Active: {len(self.market_connections)}")

    def disconnect(self, websocket: WebSocket, channel: str = "market"):
        if channel == "market" and websocket in self.market_connections:
            self.market_connections.remove(websocket)
        elif channel == "chat" and websocket in self.chat_connections:
            self.chat_connections.remove(websocket)
        elif channel == "notifications" and websocket in self.notification_connections:
            self.notification_connections.remove(websocket)
        logger.info(f"WebSocket client disconnected from channel '{channel}'.")

    async def broadcast_market(self, message: Dict[str, Any]):
        dead_connections = []
        for connection in self.market_connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.append(connection)
        for dead in dead_connections:
            if dead in self.market_connections:
                self.market_connections.remove(dead)

    async def broadcast_notification(self, message: Dict[str, Any]):
        dead_connections = []
        for connection in self.notification_connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.append(connection)
        for dead in dead_connections:
            if dead in self.notification_connections:
                self.notification_connections.remove(dead)

ws_manager = WebSocketManager()
