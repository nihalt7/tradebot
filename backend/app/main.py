import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection
from app.services.market_data import market_data_service
from app.services.scanner import scanner_service
from app.services.websocket_manager import ws_manager
from app.services.notifications import notification_service
from app.services.ai_assistant import ai_assistant_service

# Routers
from app.routes.auth import router as auth_router
from app.routes.market import router as market_router
from app.routes.watchlist import router as watchlist_router
from app.routes.scanner import router as scanner_router
from app.routes.signals import router as signals_router
from app.routes.paper_trading import router as paper_trading_router
from app.routes.risk import router as risk_router
from app.routes.backtest import router as backtest_router
from app.routes.chat import router as chat_router
from app.routes.notifications import router as notifications_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("tradebot.main")

scheduler = AsyncIOScheduler()

async def background_market_scanner():
    """Periodic task running background scans and broadcasting updates"""
    try:
        logger.info("Executing periodic background scanner...")
        scan_res = await scanner_service.scan_market()
        overview = await market_data_service.get_market_overview()
        
        # Broadcast latest overview to market websocket clients
        await ws_manager.broadcast_market({
            "type": "MARKET_TICK",
            "overview": overview,
            "top_buy": scan_res["top_buy"][:3],
            "top_sell": scan_res["top_sell"][:3]
        })
        
        # If new 80+ score signal detected, trigger notification
        for sig in scan_res["top_buy"][:2]:
            if sig["setup_score"] >= 80:
                notif = notification_service.add_notification(
                    title=f"High-Quality BUY Alert: {sig['symbol']}",
                    message=f"Setup Score: {sig['setup_score']}/100 ({sig['classification']}). Entry: ₹{sig['entry_price']}, SL: ₹{sig['stop_loss']}, T1: ₹{sig['target1']}",
                    notif_type="BUY_ALERT",
                    symbol=sig["symbol"],
                    data={"signal_id": sig["id"], "score": sig["setup_score"]}
                )
                if notif:
                    await ws_manager.broadcast_notification(notif)
                    
        for sig in scan_res["top_sell"][:2]:
            if sig["setup_score"] >= 80:
                notif = notification_service.add_notification(
                    title=f"High-Quality SELL Alert: {sig['symbol']}",
                    message=f"Setup Score: {sig['setup_score']}/100 ({sig['classification']}). Entry: ₹{sig['entry_price']}, SL: ₹{sig['stop_loss']}, T1: ₹{sig['target1']}",
                    notif_type="SELL_ALERT",
                    symbol=sig["symbol"],
                    data={"signal_id": sig["id"], "score": sig["setup_score"]}
                )
                if notif:
                    await ws_manager.broadcast_notification(notif)

    except Exception as e:
        logger.error(f"Error in background market scanner: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Trade Bot AI Engine...")
    await connect_to_mongo()
    
    # Pre-warm market data in background
    asyncio.create_task(market_data_service.get_market_overview())
    
    # Start scheduler
    scheduler.add_job(background_market_scanner, 'interval', seconds=settings.SCANNER_INTERVAL_SECONDS)
    scheduler.start()
    
    yield
    
    # Shutdown
    scheduler.shutdown(wait=False)
    await close_mongo_connection()
    logger.info("Trade Bot AI Engine shutdown cleanly.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Advanced AI-Powered Indian Stock Market Analysis & Trading Platform",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register REST Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(market_router, prefix=settings.API_V1_STR)
app.include_router(watchlist_router, prefix=settings.API_V1_STR)
app.include_router(scanner_router, prefix=settings.API_V1_STR)
app.include_router(signals_router, prefix=settings.API_V1_STR)
app.include_router(paper_trading_router, prefix=settings.API_V1_STR)
app.include_router(risk_router, prefix=settings.API_V1_STR)
app.include_router(backtest_router, prefix=settings.API_V1_STR)
app.include_router(chat_router, prefix=settings.API_V1_STR)
app.include_router(notifications_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "app": "Trade Bot AI",
        "status": "ONLINE",
        "market": market_data_service.is_market_open(),
        "documentation": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "data_status": market_data_service._data_status,
        "is_open": market_data_service.is_market_open()["is_open"]
    }

# WebSockets
@app.websocket("/ws/market")
async def websocket_market(websocket: WebSocket):
    await ws_manager.connect(websocket, "market")
    try:
        overview = await market_data_service.get_market_overview()
        await websocket.send_json({"type": "INITIAL_STATE", "overview": overview})
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, "market")

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await ws_manager.connect(websocket, "chat")
    try:
        while True:
            data = await websocket.receive_json()
            user_msg = data.get("message", "")
            session_id = data.get("session_id", "default")
            bot_reply = await ai_assistant_service.process_message(user_msg, session_id)
            await websocket.send_json(bot_reply)
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, "chat")

@app.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket):
    await ws_manager.connect(websocket, "notifications")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, "notifications")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
