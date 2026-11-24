from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
from jose import jwt
from datetime import datetime, timedelta
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

# In-memory users store with default demo user
USERS_DB = {
    "trader@tradebot.ai": {
        "id": "usr_trader_01",
        "username": "ProTrader",
        "email": "trader@tradebot.ai",
        "password": "password123",
        "created_at": "2026-01-01 09:15:00 IST"
    }
}

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

@router.post("/register")
async def register(user: UserRegister):
    if user.email in USERS_DB:
        raise HTTPException(status_code=400, detail="User already exists with this email")
        
    user_record = {
        "id": f"usr_{int(datetime.now().timestamp())}",
        "username": user.username,
        "email": user.email,
        "password": user.password,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    USERS_DB[user.email] = user_record
    token = create_access_token({"sub": user.email, "username": user.username})
    return {
        "success": True,
        "message": "User registered successfully",
        "token": token,
        "user": {"id": user_record["id"], "username": user.username, "email": user.email}
    }

@router.post("/login")
async def login(credentials: UserLogin):
    user = USERS_DB.get(credentials.email)
    if not user or user["password"] != credentials.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")
        
    token = create_access_token({"sub": user["email"], "username": user["username"]})
    return {
        "success": True,
        "token": token,
        "user": {"id": user["id"], "username": user["username"], "email": user["email"]}
    }

@router.get("/me")
async def get_current_user():
    user = USERS_DB["trader@tradebot.ai"]
    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"]
    }
