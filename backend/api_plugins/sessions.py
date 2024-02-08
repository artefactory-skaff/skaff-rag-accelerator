from datetime import datetime
from typing import List, Optional, Sequence
from uuid import uuid4

from fastapi import APIRouter, Depends, FastAPI

from backend.api_plugins.lib.user_management import User


def session_routes(
    app: FastAPI | APIRouter,
    *,
    authentication: Depends = None,
    dependencies: Optional[Sequence[Depends]] = None,
):
    from backend.database import Database
    from backend.model import Message

    @app.post("/session/new")
    async def chat_new(current_user: User=authentication, dependencies=dependencies) -> dict:
        chat_id = str(uuid4())
        timestamp = datetime.utcnow().isoformat()
        user_id = current_user.email if current_user else "unauthenticated"
        with Database() as connection:
            connection.execute(
                "INSERT INTO session (id, timestamp, user_id) VALUES (?, ?, ?)",
                (chat_id, timestamp, user_id),
            )
        return {"chat_id": chat_id}


    @app.get("/session/list")
    async def chat_list(current_user: User=authentication, dependencies=dependencies) -> List[dict]:
        user_email = current_user.email if current_user else "unauthenticated"
        chats = []
        with Database() as connection:
            result = connection.execute(
                "SELECT id, timestamp FROM session WHERE user_id = ? ORDER BY timestamp DESC",
                (user_email,),
            )
            chats = [{"id": row[0], "timestamp": row[1]} for row in result]
        return chats


    @app.get("/session/{session_id}")
    async def chat(session_id: str, dependencies=dependencies) -> dict:
        messages: List[Message] = []
        with Database() as connection:
            result = connection.execute(
                "SELECT id, timestamp, session_id, sender, content FROM message_history WHERE session_id = ? ORDER BY timestamp ASC",
                (session_id,),
            )
            for row in result:
                message = Message(
                    id=row[0],
                    timestamp=row[1],
                    chat_id=row[2],
                    sender=row[3],
                    content=row[4]
                )
                messages.append(message)
        return {"chat_id": session_id, "messages": [message.model_dump() for message in messages]}
