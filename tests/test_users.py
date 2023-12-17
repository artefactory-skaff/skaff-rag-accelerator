import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from database.database import Database
from main import app

os.environ["TESTING"] = "True"
client = TestClient(app)


@pytest.fixture()
def initialize_database() -> Database:
    """Initialize the test database by applying the initialization SQL script."""
    db = Database()
    with db:
        db.query_from_file(Path(__file__).parents[1] / "database" / "database_init.sql")
    yield db
    db.delete_db()


def test_signup(initialize_database: Database) -> None:
    """Test the user signup process."""
    response = client.post(
        "/user/signup", json={"email": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

    response = client.post(
        "/user/signup", json={"email": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == 400
    assert "detail" in response.json()
    assert response.json()["detail"] == "User test@example.com already registered"


def test_login(initialize_database: Database) -> None:
    """Test the user login process."""
    response = client.post(
        "/user/signup", json={"email": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
    response = client.post(
        "/user/login", data={"username": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_user_me(initialize_database: Database) -> None:
    """Test the retrieval of user profile information."""
    response = client.post(
        "/user/signup", json={"email": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

    response = client.post(
        "/user/login", data={"username": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

    token = response.json()["access_token"]
    response = client.get("/user/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
