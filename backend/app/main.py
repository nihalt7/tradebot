import os
import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.core.database import MongoManager, get_database
from backend.app.core.security import get_password_hash
from backend.app.market_data.simulator import MarketSimulator
from backend.app.market_data.nse_provider import market_provider
from backend.app.engines.watchlist_engine import WatchlistEngine
from backend.app.engines.scanner_engine import ScannerEngine
from backend.app.websocket.connection_manager import ws_manager

from backend.app.api import auth, chat, watchlist, scanner, signals, dashboard, risk, backtest

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("TradePulseAI")

watchlist_engine = WatchlistEngine(market_provider)
scanner_engine = ScannerEngine(market_provider)
simulator = MarketSimulator()

background_task_running = True

async def background_monitoring_loop():
    """Continuous background loop driving market simulation, Engine A (Watchlist), and Engine B (Scanner)."""
    logger.info("Starting TradePulse Dual Monitoring Engine background task (MongoDB-backed)...")
    tick_counter = 0
    
    while background_task_running:
        try:
            # 1. Update Market Simulation ticks (every 2.5 seconds)
            simulator.tick()
            tick_counter += 1

            # Broadcast market tick every 3 seconds to connected WebSocket clients
            if tick_counter % 2 == 0:
                overview = simulator.get_market_overview()
                await ws_manager.broadcast_market_tick(overview)

            # 2. Engine A: Personal Watchlist Monitoring (Every 15 seconds)
            if tick_counter % 6 == 0:
                db = get_database()
                user = db.users.find_one({})
                user_id = user["id"] if user else 1
                watched_stocks = db.watchlists.find({"user_id": user_id})

                for w in watched_stocks:
                    opp = watchlist_engine.analyze_stock(w["symbol"])
                    if opp and opp.get("setup_score", 0) >= 78.0:
                        recent_sig = db.trading_signals.find_one({
                            "symbol": w["symbol"],
                            "status": "ACTIVE"
                        })
                        
                        if not recent_sig:
                            sig_id = f"SIG_{w['symbol']}_{int(datetime.now().timestamp())}"
                            sig_doc = {
                                "id": sig_id,
                                "symbol": w["symbol"],
                                "exchange": "NSE",
                                "signal_type": opp["signal"],
                                "source_engine": "WATCHLIST",
                                "entry_min": opp["entry_min"],
                                "entry_max": opp["entry_max"],
                                "stop_loss": opp["stop_loss"],
                                "target_1": opp["target_1"],
                                "target_2": opp["target_2"],
                                "target_3": opp["target_3"],
                                "risk_reward": opp["breakdown"].get("risk_reward_quality", 2.0),
                                "setup_score": opp["setup_score"],
                                "timeframe": "5m",
                                "status": "ACTIVE",
                                "generated_at": datetime.utcnow(),
                                "expires_at": datetime.utcnow(),
                                "reason": opp["reason"]
                            }
                            db.trading_signals.insert_one(sig_doc)

                            card_data = {
                                "id": sig_id,
                                "symbol": opp["symbol"],
                                "exchange": "NSE",
                                "signal": opp["signal"],
                                "entry_min": opp["entry_min"],
                                "entry_max": opp["entry_max"],
                                "stop_loss": opp["stop_loss"],
                                "target_1": opp["target_1"],
                                "target_2": opp["target_2"],
                                "target_3": opp["target_3"],
                                "rsi": opp["rsi"],
                                "vwap_status": opp["vwap_status"],
                                "ema_status": opp["ema_status"],
                                "macd_status": opp["macd_status"],
                                "volume_ratio": opp["volume_ratio"],
                                "timeframe": "5 Minutes",
                                "setup_score": opp["setup_score"],
                                "risk_reward": opp["risk_reward"],
                                "signal_time": opp["signal_time"],
                                "validity_minutes": 5,
                                "reason": opp["reason"],
                                "suggested_qty": 350
                            }

                            msg_count = db.chat_messages.count_documents({})
                            chat_msg_doc = {
                                "id": msg_count + 1,
                                "conversation_id": "main_chat",
                                "sender": "assistant",
                                "text": f"🚨 **HIGH-QUALITY TRADING OPPORTUNITY (ENGINE A: WATCHLIST)**\n\nStock: **{w['symbol']}** | Signal: **{opp['signal']}** | Score: **{opp['setup_score']}/100**",
                                "message_type": "signal_card",
                                "card_data": card_data,
                                "timestamp": datetime.utcnow()
                            }
                            db.chat_messages.insert_one(chat_msg_doc)

                            await ws_manager.broadcast_signal_alert(card_data)
                            await ws_manager.send_user_message(user_id, {
                                "id": chat_msg_doc["id"],
                                "conversation_id": "main_chat",
                                "sender": "assistant",
                                "text": chat_msg_doc["text"],
                                "message_type": "signal_card",
                                "card_data": card_data,
                                "timestamp": chat_msg_doc["timestamp"].isoformat()
                            })

            # 3. Engine B: Automatic NSE Universe Scanner (Every 25 seconds)
            if tick_counter % 10 == 0:
                scanner_engine.run_market_scan()

        except Exception as e:
            logger.error(f"Error in background monitoring loop: {e}", exc_info=True)

        await asyncio.sleep(2.5)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize MongoDB Atlas connection
    logger.info("Initializing MongoDB Atlas connection manager...")
    MongoManager.initialize()
    
    db = get_database()
    user = db.users.find_one({})
    if not user:
        user_doc = {
            "id": 1,
            "username": "trader",
            "email": "trader@tradepulse.ai",
            "full_name": "Pro Intraday Trader",
            "hashed_password": get_password_hash("trader123"),
            "is_active": True,
            "is_admin": False,
            "created_at": datetime.utcnow()
        }
        db.users.insert_one(user_doc)

        db.risk_settings.insert_one({
            "user_id": 1,
            "capital": 500000.0,
            "risk_per_trade_pct": 1.0,
            "max_daily_loss": 15000.0,
            "current_daily_loss": 0.0,
            "max_open_trades": 5,
            "paper_trading_enabled": True,
            "trading_halted": False,
            "updated_at": datetime.utcnow()
        })

        db.conversations.insert_one({
            "id": "main_chat",
            "user_id": 1,
            "title": "AI Trading Assistant",
            "category": "chat",
            "created_at": datetime.utcnow()
        })
        db.conversations.insert_one({
            "id": "watchlist_feed",
            "user_id": 1,
            "title": "Engine A: Watchlist Alerts",
            "category": "watchlist_alerts",
            "created_at": datetime.utcnow()
        })
        db.conversations.insert_one({
            "id": "scanner_feed",
            "user_id": 1,
            "title": "Engine B: NSE Scanner Feed",
            "category": "scanner_feed",
            "created_at": datetime.utcnow()
        })
        
        for idx, sym in enumerate(["RELIANCE", "TCS", "HDFCBANK", "INFY"]):
            db.watchlists.insert_one({
                "id": idx + 1,
                "user_id": 1,
                "symbol": sym,
                "exchange": "NSE",
                "notes": "Core bluechip",
                "added_at": datetime.utcnow()
            })

    # Cache scan once
    scanner_engine.run_market_scan()

    # Launch background task
    monitor_task = asyncio.create_task(background_monitoring_loop())
    
    yield

    # Shutdown
    global background_task_running
    background_task_running = False
    monitor_task.cancel()
    try:
        await monitor_task
    except asyncio.CancelledError:
        pass
    if MongoManager.client:
        MongoManager.client.close()
    logger.info("TradePulse background engines stopped.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Advanced AI-Powered Indian Stock Market Quant Platform with WhatsApp Web-Style Chat Interface",
    lifespan=lifespan
)

# CORS configuration for Vercel deployment
cors_origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
if not cors_origins or cors_origins == ["*"]:
    cors_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount REST API Routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(chat.router, prefix=f"{settings.API_V1_STR}/chat", tags=["AI Chat"])
app.include_router(watchlist.router, prefix=f"{settings.API_V1_STR}/watchlist", tags=["Engine A: Watchlist"])
app.include_router(scanner.router, prefix=f"{settings.API_V1_STR}/scanner", tags=["Engine B: Scanner"])
app.include_router(signals.router, prefix=f"{settings.API_V1_STR}/signals", tags=["Signals & Orders"])
app.include_router(dashboard.router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["Market Dashboard"])
app.include_router(risk.router, prefix=f"{settings.API_V1_STR}/risk", tags=["Risk Management"])
app.include_router(backtest.router, prefix=f"{settings.API_V1_STR}/backtest", tags=["Strategy Backtest"])

@app.get("/")
def root():
    return {
        "platform": settings.PROJECT_NAME,
        "database": "MongoDB Atlas" if MongoManager.is_atlas else "MongoDB (Local/Fallback)",
        "status": "ONLINE",
        "engines": {
            "engine_a_watchlist": "ACTIVE",
            "engine_b_nse_scanner": "ACTIVE"
        },
        "docs": "/docs"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "database": "connected" if MongoManager.client or MongoManager.db else "degraded",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.websocket("/ws/market")
async def websocket_market_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.warning(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=port, reload=False)
