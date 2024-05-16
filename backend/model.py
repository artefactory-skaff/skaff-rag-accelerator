from datetime import datetime
from typing import List, Union
from uuid import uuid4

from pydantic import BaseModel, Field


class Message(BaseModel):
    id: str
    timestamp: Union[str, datetime]
    session_id: str
    sender: str
    content: str


class Input(BaseModel):
    question: str


class InvokeRequest(BaseModel):
    input: Input | List[Input]  # Supports batched input
    id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str = None
    config: dict = Field(default_factory=dict)
    kwargs: dict = Field(default_factory=dict)
    timestamp: str | datetime = Field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )


class UserMessage(InvokeRequest):
    sender: str = "user"
