from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from backend.app.core.database import get_database
from backend.app.core.security import get_password_hash, verify_password, create_access_token
from backend.app.core.config import settings
from backend.app.schemas.schemas import UserCreate, UserResponse, LoginRequest, Token

router = APIRouter()

@router.post("/register", response_model=Token)
def register(user_in: UserCreate):
    db = get_database()
    existing = db.users.find_one({"$or": [{"username": user_in.username}, {"email": user_in.email}]})
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    
    user_count = db.users.count_documents({})
    user_id = user_count + 1

    user_doc = {
        "id": user_id,
        "username": user_in.username,
        "email": user_in.email,
        "full_name": user_in.full_name or user_in.username,
        "hashed_password": get_password_hash(user_in.password),
        "is_active": True,
        "is_admin": False,
        "created_at": datetime.utcnow()
    }
    db.users.insert_one(user_doc)

    # Initialize default risk settings for user in MongoDB
    db.risk_settings.insert_one({
        "user_id": user_id,
        "capital": settings.DEFAULT_CAPITAL,
        "risk_per_trade_pct": settings.DEFAULT_RISK_PER_TRADE_PCT,
        "max_daily_loss": settings.DEFAULT_MAX_DAILY_LOSS,
        "current_daily_loss": 0.0,
        "max_open_trades": settings.DEFAULT_MAX_OPEN_TRADES,
        "paper_trading_enabled": True,
        "trading_halted": False,
        "updated_at": datetime.utcnow()
    })

    # Initialize main conversation in MongoDB
    db.conversations.insert_one({
        "id": "main_chat",
        "user_id": user_id,
        "title": "TradePulse AI Quant Chat",
        "category": "chat",
        "created_at": datetime.utcnow()
    })

    token = create_access_token(user_id)
    return Token(access_token=token, token_type="bearer", user=UserResponse.model_validate(user_doc))

@router.post("/login", response_model=Token)
def login(login_req: LoginRequest):
    db = get_database()
    user = db.users.find_one({"username": login_req.username})
    if not user or not verify_password(login_req.password, user.get("hashed_password", "")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    
    token = create_access_token(user["id"])
    return Token(access_token=token, token_type="bearer", user=UserResponse.model_validate(user))

@router.get("/me", response_model=UserResponse)
def get_me():
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
            "trading_halted": False
        })
        db.conversations.insert_one({
            "id": "main_chat",
            "user_id": 1,
            "title": "TradePulse AI Quant Chat",
            "category": "chat",
            "created_at": datetime.utcnow()
        })
        user = user_doc
    return UserResponse.model_validate(user)
