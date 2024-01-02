from pydantic import BaseModel


class Message(BaseModel):
    id: str
    timestamp: str
    chat_id: str
    sender: str
    content: str
