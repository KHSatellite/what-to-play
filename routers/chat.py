import asyncio
from uuid import UUID
import jwt
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from config import settings
from database import SessionLocal
from repositories.user_repository import UserRepository
from services.chat_bot import ChatBot

router = APIRouter(tags=["chat"])


def _user_from_token(db, token: str | None):
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return UserRepository(db).get_by_id(UUID(payload["sub"]))
    except Exception:
        return None


@router.websocket("/ws/chat")
async def chat_websocket(websocket: WebSocket, token: str | None = None, lang: str = "tr"):
    await websocket.accept()
    db = SessionLocal()
    try:
        user = _user_from_token(db, token)
        bot = ChatBot(db, user, lang)
        await websocket.send_json({"from": "bot", "text": bot.m["hello"].format(name=bot._name())})
        while True:
            text = await websocket.receive_text()
            # DB'ye dokunan yanıtlar event loop'u bloklamasın diye thread'de üretilir
            reply = await asyncio.to_thread(bot.reply, text)
            await asyncio.sleep(min(0.3 + len(reply) / 400, 1.2))  # "yazıyor…" hissi
            await websocket.send_json({"from": "bot", "text": reply})
    except WebSocketDisconnect:
        pass
    finally:
        db.close()
