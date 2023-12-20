import os
from pathlib import Path
from typing import Generator, Tuple

import pytest
from fastapi.testclient import TestClient
from lib.main import app

from database.database import Database

os.environ["TESTING"] = "True"
client = TestClient(app)


@pytest.fixture(scope="module")
def context() -> Generator[Tuple[dict, Database], None, None]:
    """Set up the database context and provides a client with an authorized header."""
    db = Database()
    with db:
        db.query_from_file(Path(__file__).parents[1] / "database" / "database_init.sql")

    user_data = {"email": "test@example.com", "password": "testpassword"}

    response = client.post("/user/signup", json=user_data)
    assert response.status_code == 200
    response = client.post(
        "/user/login", data={"username": user_data["email"], "password": user_data["password"]}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}

    yield client.headers, db
    db.delete_db()


def test_feedback_thumbs_up(context: Tuple[dict, Database]) -> None:
    """Test to ensure that giving a thumbs up feedback works correctly."""
    headers, db = context[0], context[1]
    message_id = "test_message_id_1"
    response = client.post(f"/feedback/{message_id}/thumbs_up", headers=headers)
    assert response.status_code == 200
    with db:
        result = db.query("SELECT 1 FROM feedback WHERE message_id = ?", (message_id,))[0]
    assert len(result) == 1


def test_feedback_thumbs_down(context: Tuple[dict, Database]) -> None:
    """Test to ensure that giving a thumbs down feedback works correctly."""
    headers, db = context[0], context[1]
    message_id = "test_message_id_2"
    response = client.post(f"/feedback/{message_id}/thumbs_down", headers=headers)
    assert response.status_code == 200
    with db:
        result = db.query("SELECT 1 FROM feedback WHERE message_id = ?", (message_id,))[0]
    assert len(result) == 1
