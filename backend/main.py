import asyncio
import inspect
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import List
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from langchain_core.messages.ai import AIMessage, AIMessageChunk

from backend.database import Database
from backend.logger import get_logger
from backend.model import Message
from backend.rag_components.rag import RAG
from backend.user_management import (
    ALGORITHM,
    SECRET_KEY,
    User,
    authenticate_user,
    create_access_token,
    create_user,
    get_user,
    user_exists,
)

app = FastAPI()
logger = get_logger()

with Database() as connection:
    connection.initialize_schema()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("email")
        if email is None:
            raise credentials_exception

        user = get_user(email)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


############################################
###               Chat                   ###
############################################

@app.post("/chat/new")
async def chat_new(current_user: User = Depends(get_current_user)) -> dict:
    chat_id = str(uuid4())
    timestamp = datetime.now().isoformat()
    user_id = current_user.email
    with Database() as connection:
        connection.execute(
            "INSERT INTO chat (id, timestamp, user_id) VALUES (?, ?, ?)",
            (chat_id, timestamp, user_id),
        )
    return {"chat_id": chat_id}


@app.post("/chat/{chat_id}/user_message")
async def chat_prompt(message: Message, current_user: User = Depends(get_current_user)) -> dict:
    with Database() as connection:
        connection.execute(
            "INSERT INTO message (id, timestamp, chat_id, sender, content) VALUES (?, ?, ?, ?, ?)",
            (message.id, message.timestamp, message.chat_id, message.sender, message.content),
        )

    context = {
        "user": current_user.email,
        "chat_id": message.chat_id,
        "message_id": message.id,
        "timestamp": message.timestamp,
    }
    rag = RAG(config=Path(__file__).parent / "config.yaml", logger=logger, context=context)
    response = rag.generate_response(message)
    return StreamingResponse(stream_response(message.chat_id, response), media_type="text/event-stream")


@app.post("/chat/regenerate")
async def chat_regenerate(current_user: User = Depends(get_current_user)) -> dict:
    """Regenerate a chat session for the current user."""
    pass


@app.get("/chat/list")
async def chat_list(current_user: User = Depends(get_current_user)) -> List[dict]:
    chats = []
    with Database() as connection:
        result = connection.execute(
            "SELECT id, timestamp FROM chat WHERE user_id = ? ORDER BY timestamp DESC",
            (current_user.email,),
        )
        chats = [{"id": row[0], "timestamp": row[1]} for row in result]
    return chats


@app.get("/chat/{chat_id}")
async def chat(chat_id: str, current_user: User = Depends(get_current_user)) -> dict:
    messages: List[Message] = []
    with Database() as connection:
        result = connection.execute(
            "SELECT id, timestamp, chat_id, sender, content FROM message WHERE chat_id = ? ORDER BY timestamp ASC",
            (chat_id,),
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
    return {"chat_id": chat_id, "messages": [message.model_dump() for message in messages]}


async def stream_response(chat_id: str, response):
    full_response = ""
    response_id = str(uuid4())
    try:
        if type(response) is AIMessage:
            full_response = response.content
            yield full_response.encode("utf-8")
        elif inspect.isasyncgen(response):
            async for data in response:
                full_response += data.content
                yield data.content.encode("utf-8")
        else:
            for part in response:
                if isinstance(part, AIMessageChunk):
                    part = part.content
                full_response += part
                yield part.encode("utf-8")
                await asyncio.sleep(0)
    except Exception as e:
        logger.error(f"Error generating response for chat {chat_id}: {e}", exc_info=True)
        full_response = f"Sorry, there was an error generating a response. Please contact an administrator and provide them with the following error code: {response_id} \n\n {traceback.format_exc()}"
        yield full_response.encode("utf-8")
    finally:
        await log_response_to_db(chat_id, full_response)

async def log_response_to_db(chat_id: str, full_response: str):
    response_id = str(uuid4())
    with Database() as connection:
        connection.execute(
            "INSERT INTO message (id, timestamp, chat_id, sender, content) VALUES (?, ?, ?, ?, ?)",
            (response_id, datetime.now().isoformat(), chat_id, "assistant", full_response),
        )


############################################
###               Feedback               ###
############################################

@app.post("/feedback/{message_id}/thumbs_up")
async def feedback_thumbs_up(
    message_id: str, current_user: User = Depends(get_current_user)
) -> None:
    with Database() as connection:
        connection.execute(
            "INSERT INTO feedback (id, message_id, feedback) VALUES (?, ?, ?)",
            (str(uuid4()), message_id, "thumbs_up"),
        )


@app.post("/feedback/{message_id}/thumbs_down")
async def feedback_thumbs_down(
    message_id: str, current_user: User = Depends(get_current_user)
) -> None:
    with Database() as connection:
        connection.execute(
            "INSERT INTO feedback (id, message_id, feedback) VALUES (?, ?, ?)",
            (str(uuid4()), message_id, "thumbs_down"),
        )


############################################
###           Authentication             ###
############################################


@app.post("/user/signup")
async def signup(user: User) -> dict:
    if user_exists(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"User {user.email} already registered"
        )

    create_user(user)
    return {"email": user.email}


@app.delete("/user/")
async def delete_user(current_user: User = Depends(get_current_user)) -> dict:
    email = current_user.email
    try:
        user = get_user(email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"User {email} not found"
            )
        delete_user(email)
        return {"detail": f"User {email} deleted"}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error"
        )


@app.post("/user/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(data=user.model_dump(), expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/user/me")
async def user_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
