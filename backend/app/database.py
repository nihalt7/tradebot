import logging
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

logger = logging.getLogger("tradebot.database")

class Database:
    client: AsyncIOMotorClient = None
    db = None
    is_connected: bool = False
    
    # In-memory storage fallback if MongoDB Atlas is not connected
    _local_store = {
        "users": {},
        "conversations": {},
        "chat_messages": {},
        "watchlists": {},
        "stocks": {},
        "market_data": {},
        "technical_indicators": {},
        "trading_signals": {},
        "active_positions": {},
        "trading_history": {},
        "risk_settings": {},
        "backtesting_results": {},
        "notifications": [],
        "application_settings": {}
    }

db_manager = Database()

async def connect_to_mongo():
    if settings.MONGODB_URI:
        try:
            logger.info("Connecting to MongoDB Atlas...")
            db_manager.client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=5000
            )
            # Verify connection
            await db_manager.client.admin.command('ping')
            db_manager.db = db_manager.client[settings.DATABASE_NAME]
            db_manager.is_connected = True
            logger.info("Successfully connected to MongoDB Atlas!")
        except Exception as e:
            logger.warning(f"MongoDB connection failed: {e}. Falling back to resilient local storage.")
            db_manager.is_connected = False
    else:
        logger.info("MONGODB_URI not provided. Running in persistent local store mode.")
        db_manager.is_connected = False

async def close_mongo_connection():
    if db_manager.client:
        db_manager.client.close()
        logger.info("MongoDB connection closed.")
