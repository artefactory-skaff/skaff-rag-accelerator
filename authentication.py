import os
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from pydantic import BaseModel

from database.database import Database

SECRET_KEY = os.environ.get("SECRET_KEY", "default_unsecure_key")
ALGORITHM = "HS256"


class User(BaseModel):
    """Represents a user with an email and password."""

    email: str = None
    password: str = None


def create_user(user: User) -> None:
    """Create a new user in the database."""
    with Database() as connection:
        connection.query(
            "INSERT INTO user (email, password) VALUES (?, ?)", (user.email, user.password)
        )


def get_user(email: str) -> User:
    """Retrieve a user from the database by email."""
    with Database() as connection:
        user_row = connection.query("SELECT * FROM user WHERE email = ?", (email,))[0]
        for row in user_row:
            return User(**row)
        raise Exception("User not found")


def authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticate a user by their username and password."""
    user = get_user(username)
    if not user or not password == user.password:
        return False
    return user


def create_access_token(*, data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token with optional expiry."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
