from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter
from backend.app.core.database import get_database
from backend.app.schemas.schemas import ChatMessageCreate, ChatMessageResponse
from backend.app.engines.ai_chat_analyst import AIChatAnalyst
from backend.app.engines.scanner_engine import ScannerEngine
from backend.app.market_data.nse_provider import market_provider
from backend.app.websocket.connection_manager import ws_manager

router = APIRouter()
scanner_engine = ScannerEngine(market_provider)
chat_analyst = AIChatAnalyst(market_provider, scanner_engine)

@router.get("/conversations")
def get_conversations():
    db = get_database()
    user = db.users.find_one({})
    user_id = user["id"] if user else 1

    convs = db.conversations.find({"user_id": user_id})
    if not convs:
        # Create default channels in MongoDB
        c1 = {"id": "main_chat", "user_id": user_id, "title": "AI Trading Assistant", "category": "chat", "created_at": datetime.utcnow()}
        c2 = {"id": "watchlist_feed", "user_id": user_id, "title": "Engine A: Watchlist Alerts", "category": "watchlist_alerts", "created_at": datetime.utcnow()}
        c3 = {"id": "scanner_feed", "user_id": user_id, "title": "Engine B: NSE Scanner Feed", "category": "scanner_feed", "created_at": datetime.utcnow()}
        db.conversations.insert_one(c1)
        db.conversations.insert_one(c2)
        db.conversations.insert_one(c3)
        convs = [c1, c2, c3]
    
    res = []
    for c in convs:
        last_msg = db.chat_messages.find_one(
            {"conversation_id": c["id"]},
            sort=[("timestamp", -1)]
        )
        t_str = "Now"
        if last_msg and "timestamp" in last_msg:
            t = last_msg["timestamp"]
            t_str = t.strftime("%I:%M %p") if isinstance(t, datetime) else str(t)

        res.append({
            "id": c["id"],
            "title": c["title"],
            "category": c.get("category", "chat"),
            "last_message": last_msg["text"] if last_msg else "Ready to analyze NSE opportunities.",
            "last_time": t_str,
            "unread_count": 0
        })
    return res

@router.get("/messages/{conversation_id}", response_model=List[ChatMessageResponse])
def get_messages(conversation_id: str, limit: int = 50):
    db = get_database()
    msgs = db.chat_messages.find(
        {"conversation_id": conversation_id},
        sort=[("timestamp", 1)],
        limit=limit
    )

    if not msgs and conversation_id == "main_chat":
        welcome = {
            "id": 1,
            "conversation_id": "main_chat",
            "sender": "assistant",
            "text": (
                "👋 **Welcome to TradePulse AI Trading Assistant!**\n\n"
                "I am your dedicated real-time Indian Stock Market quantitative analyst.\n"
                "• **Engine A (Personal Watchlist):** Type `ADD <SYMBOL>` (e.g. `ADD RELIANCE`) to monitor your favorite stocks.\n"
                "• **Engine B (NSE Scanner):** Automatically identifies Top 5 BUY/SELL setups, breakouts, and unusual volume.\n"
                "• **The Golden Rule:** *No high-quality opportunity = No message.* Only confirmed setups (Score ≥ 75) trigger alerts.\n\n"
                "Try typing: `TOP 5`, `ANALYZE RELIANCE`, `SCAN`, or `HELP`."
            ),
            "message_type": "text",
            "card_data": None,
            "timestamp": datetime.utcnow()
        }
        db.chat_messages.insert_one(welcome)
        msgs = [welcome]

    result = []
    for m in msgs:
        result.append(ChatMessageResponse(
            id=m.get("id", 1),
            conversation_id=m.get("conversation_id", conversation_id),
            sender=m.get("sender", "assistant"),
            text=m.get("text", ""),
            message_type=m.get("message_type", "text"),
            card_data=m.get("card_data"),
            timestamp=m.get("timestamp") if isinstance(m.get("timestamp"), datetime) else datetime.utcnow()
        ))
    return result

@router.post("/send", response_model=ChatMessageResponse)
async def send_message(msg_in: ChatMessageCreate):
    db = get_database()
    user = db.users.find_one({})
    user_id = user["id"] if user else 1

    msg_count = db.chat_messages.count_documents({})

    # 1. Store user message in MongoDB
    user_msg_doc = {
        "id": msg_count + 1,
        "conversation_id": msg_in.conversation_id,
        "sender": "user",
        "text": msg_in.text,
        "message_type": "text",
        "card_data": None,
        "timestamp": datetime.utcnow()
    }
    db.chat_messages.insert_one(user_msg_doc)

    # 2. Process with AI Quant Analyst
    result = chat_analyst.process_message(user_id, msg_in.text, db)

    # 3. Store AI assistant response in MongoDB
    ai_msg_doc = {
        "id": msg_count + 2,
        "conversation_id": msg_in.conversation_id,
        "sender": "assistant",
        "text": result["text"],
        "message_type": result.get("message_type", "text"),
        "card_data": result.get("card_data"),
        "timestamp": datetime.utcnow()
    }
    db.chat_messages.insert_one(ai_msg_doc)

    # 4. Broadcast via WebSocket
    await ws_manager.send_user_message(user_id, {
        "id": ai_msg_doc["id"],
        "conversation_id": ai_msg_doc["conversation_id"],
        "sender": ai_msg_doc["sender"],
        "text": ai_msg_doc["text"],
        "message_type": ai_msg_doc["message_type"],
        "card_data": ai_msg_doc["card_data"],
        "timestamp": ai_msg_doc["timestamp"].isoformat()
    })

    return ChatMessageResponse.model_validate(ai_msg_doc)

@router.delete("/messages/{conversation_id}/clear")
def clear_messages(conversation_id: str):
    db = get_database()
    db.chat_messages.delete_many({"conversation_id": conversation_id})
    return {"status": "cleared"}
