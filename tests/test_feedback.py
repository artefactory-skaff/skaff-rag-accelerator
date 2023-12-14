import os
os.environ["TESTING"] = "True"

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from database.database import Database
from main import app


client = TestClient(app)

@pytest.fixture(scope="module")
def context():
    db = Database()
    with db:
        db.query_from_file(Path(__file__).parents[1] / "database" / "database_init.sql")

    user_data = {
        "email": "test@example.com",
        "password": "testpassword"
    }
    
    response = client.post("/user/signup", json=user_data)
    assert response.status_code == 200
    response = client.post("/user/login", data={"username": user_data["email"], "password": user_data["password"]})
    assert response.status_code == 200
    token = response.json()["access_token"]
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    
    yield client.headers, db
    db.delete_db()

def test_feedback_thumbs_up(context):
    headers, db = context[0], context[1]
    message_id = "test_message_id_1"
    response = client.post(f"/feedback/{message_id}/thumbs_up", headers=headers)
    assert response.status_code == 200
    with db:
        result = db.query("SELECT 1 FROM feedback WHERE message_id = ?", (message_id, ))[0]
    assert len(result) == 1

def test_feedback_thumbs_down(context):
    headers, db = context[0], context[1]
    message_id = "test_message_id_2"
    response = client.post(f"/feedback/{message_id}/thumbs_down", headers=headers)
    assert response.status_code == 200
    with db:
        result = db.query("SELECT 1 FROM feedback WHERE message_id = ?", (message_id, ))[0]
    assert len(result) == 1
