from datetime import datetime
from typing import Union
from pydantic import BaseModel


class Message(BaseModel):
    id: str
    timestamp: Union[str, datetime]
    chat_id: str
    sender: str
    content: str
