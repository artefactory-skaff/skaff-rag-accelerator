from datetime import datetime
from uuid import uuid4
from langchain.docstore.document import Document
from pydantic import BaseModel

class Message(BaseModel):
    id: str
    timestamp: str
    chat_id: str
    sender: str
    content: str

class Doc(BaseModel):
    """Represents a document with content and associated metadata."""

    content: str
    metadata: dict

    def to_langchain_document(self) -> Document:
        """Converts the current Doc instance into a langchain Document."""
        return Document(page_content=self.content, metadata=self.metadata)
