from datetime import timedelta
from typing import List

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError

import document_store
from user_management import (authenticate_user, create_access_token, create_user, 
                            get_user, User, SECRET_KEY, ALGORITHM, user_exists)
from document_store import StorageBackend
from model import Doc


app = FastAPI()


############################################
###           Authentication             ###
############################################

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
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
async def signup(user: User):
    if user_exists(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User {user.email} already registered"
        )
    
    create_user(user)
    return {"email": user.email}


@app.delete("/user/")
async def delete_user(current_user: User = Depends(get_current_user)):
    email = current_user.email
    try:
        user = get_user(email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {email} not found"
            )
        delete_user(email)
        return {"detail": f"User {email} deleted"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )


@app.post("/user/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(
        data=user.model_dump(), expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/user/me")
async def user_me(current_user: User = Depends(get_current_user)):
    return current_user


############################################
###               Chat                   ###
############################################
# P1
@app.post("/chat/new")
async def chat_new(current_user: User = Depends(get_current_user)):
    pass

# P1
@app.post("/chat/user_message")
async def chat_prompt(current_user: User = Depends(get_current_user)):
    pass

@app.get("/chat/list")
async def chat_list(current_user: User = Depends(get_current_user)):
    pass

@app.get("/chat/{chat_id}")
async def chat(chat_id: str, current_user: User = Depends(get_current_user)):
    pass


############################################
###               Feedback               ###
############################################

@app.post("/feedback/thumbs_up")
async def feedback_thumbs_up(current_user: User = Depends(get_current_user)):
    pass

@app.post("/feedback/thumbs_down")
async def feedback_thumbs_down(current_user: User = Depends(get_current_user)):
    pass

@app.post("/feedback/regenerate")
async def feedback_regenerate(current_user: User = Depends(get_current_user)):
    pass


############################################
###                Other                 ###
############################################

@app.post("/index/documents")
async def index_documents(chunks: List[Doc], bucket: str, storage_backend: StorageBackend):
    document_store.store_documents(chunks, bucket, storage_backend)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)