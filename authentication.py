from datetime import timedelta, datetime
import os
from pydantic import BaseModel
from jose import jwt


from database.database import DatabaseConnection

SECRET_KEY = os.environ.get("SECRET_KEY", "default_unsecure_key")
ALGORITHM = "HS256"

class User(BaseModel):
    email: str = None
    password: str = None

def create_user(user: User):
    with DatabaseConnection() as connection:
        connection.query("INSERT INTO user (email, password) VALUES (?, ?)", (user.email, user.password))
    
def get_user(email: str):
    with DatabaseConnection() as connection:
        user_row = connection.query("SELECT * FROM user WHERE email = ?", (email,))[0]
        for row in user_row:
            return User(**row)
        raise Exception("User not found")

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user or not password == user.password:
        return False
    return user

def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
