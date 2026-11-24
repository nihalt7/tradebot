from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from app.services.ai_assistant import ai_assistant_service

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatMessageRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"

@router.get("/history")
async def get_chat_history(session_id: str = "default"):
    return {"history": ai_assistant_service.get_conversation_history(session_id)}

@router.post("/message")
async def send_chat_message(req: ChatMessageRequest):
    bot_reply = await ai_assistant_service.process_message(req.message, req.session_id)
    return bot_reply
