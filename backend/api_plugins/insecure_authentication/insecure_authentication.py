from pathlib import Path

from fastapi import Depends, HTTPException, Response, status

from backend.api_plugins.lib.user_management import (
    User,
    create_user,
    delete_user,
    get_user,
    user_exists,
)
from backend.database import Database


def insecure_authentication_routes(app):
    with Database() as connection:
        connection.run_script(Path(__file__).parent / "users_tables.sql")

    async def get_current_user(email: str) -> User:
        email = email.replace("Bearer ", "")
        user = get_user(email)
        return user

    @app.post("/user/signup")
    async def signup(email: str) -> dict:
        user = User(email=email)
        if user_exists(user.email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User {user.email} already registered")
        create_user(user)
        return {"email": user.email}


    @app.delete("/user/")
    async def del_user(current_user: User = Depends(get_current_user)) -> dict:
        email = current_user.email
        try:
            user = get_user(email)
            if user is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {email} not found")
            delete_user(email)
            return {"detail": f"User {email} deleted"}
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


    @app.post("/user/login")
    async def login(email: str) -> dict:
        user = get_user(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username",
            )
        return {"access_token": email, "token_type": "bearer"}  # Fake bearer token to still provide user authentication


    @app.get("/user/me")
    async def user_me(current_user: User = Depends(get_current_user)) -> User:
        return current_user


    @app.get("/user")
    async def user_root() -> dict:
        return Response("Insecure user management routes are enabled. Do not use in prod.", status_code=200)

    return Depends(get_current_user)
