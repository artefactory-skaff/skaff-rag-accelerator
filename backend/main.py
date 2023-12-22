from datetime import datetime, timedelta
from pathlib import Path
from typing import List
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

from backend.config_renderer import get_config
from backend.document_store import StorageBackend, store_documents
from backend.model import Doc, Message
from backend.rag_components.document_loader import generate_response
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
from database.database import Database

app = FastAPI()


############################################
###           Authentication             ###
############################################

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get the current user by decoding the JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("email")  # 'sub' is commonly used to store user identity
        if email is None:
            raise credentials_exception
        # Here you should fetch the user from the database by user_id
        user = get_user(email)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


@app.post("/user/signup")
async def signup(user: User) -> dict:
    """Sign up a new user."""
    if user_exists(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"User {user.email} already registered"
        )

    create_user(user)
    return {"email": user.email}


@app.delete("/user/")
async def delete_user(current_user: User = Depends(get_current_user)) -> dict:
    """Delete an existing user."""
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
    """Log in a user and return an access token."""
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
    """Get the current user's profile."""
    return current_user


############################################
###               Chat                   ###
############################################


@app.post("/chat/new")
async def chat_new(current_user: User = Depends(get_current_user)) -> dict:
    chat_id = str(uuid4())
    timestamp = datetime.now().isoformat()
    user_id = current_user.email
    with Database() as connection:
        connection.query(
            "INSERT INTO chat (id, timestamp, user_id) VALUES (?, ?, ?)",
            (chat_id, timestamp, user_id),
        )
    return {"chat_id": chat_id}


@app.post("/chat/{chat_id}/user_message")
async def chat_prompt(message: Message, current_user: User = Depends(get_current_user)) -> dict:
    with Database() as connection:
        connection.query(
            "INSERT INTO message (id, timestamp, chat_id, sender, content) VALUES (?, ?, ?, ?, ?)",
            (message.id, message.timestamp, message.chat_id, message.sender, message.content),
        )

    config = get_config()

    model_response = Message(
        id=str(uuid4()),
        timestamp=datetime.now().isoformat(),
        chat_id=message.chat_id,
        sender="assistant",
        content=response,
    )

    with Database() as connection:
        connection.query(
            "INSERT INTO message (id, timestamp, chat_id, sender, content) VALUES (?, ?, ?, ?, ?)",
            (
                model_response.id,
                model_response.timestamp,
                model_response.chat_id,
                model_response.sender,
                model_response.content,
            ),
        )
    return {"message": model_response}


@app.post("/chat/regenerate")
async def chat_regenerate(current_user: User = Depends(get_current_user)) -> dict:
    """Regenerate a chat session for the current user."""
    pass


@app.get("/chat/list")
async def chat_list(current_user: User = Depends(get_current_user)) -> List[dict]:
    """Get a list of chat sessions for the current user."""
    pass


@app.get("/chat/{chat_id}")
async def chat(chat_id: str, current_user: User = Depends(get_current_user)) -> dict:
    """Get details of a specific chat session."""
    pass


############################################
###               Feedback               ###
############################################


@app.post("/feedback/{message_id}/thumbs_up")
async def feedback_thumbs_up(
    message_id: str, current_user: User = Depends(get_current_user)
) -> None:
    with Database() as connection:
        connection.query(
            "INSERT INTO feedback (id, message_id, feedback) VALUES (?, ?, ?)",
            (str(uuid4()), message_id, "thumbs_up"),
        )


@app.post("/feedback/{message_id}/thumbs_down")
async def feedback_thumbs_down(
    message_id: str, current_user: User = Depends(get_current_user)
) -> None:
    with Database() as connection:
        connection.query(
            "INSERT INTO feedback (id, message_id, feedback) VALUES (?, ?, ?)",
            (str(uuid4()), message_id, "thumbs_down"),
        )


############################################
###                Other                 ###
############################################


@app.post("/index/documents")
async def index_documents(chunks: List[Doc], bucket: str, storage_backend: StorageBackend) -> None:
    """Index documents in a specified storage backend."""
    store_documents(chunks, bucket, storage_backend)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
