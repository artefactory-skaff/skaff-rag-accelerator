from langchain.docstore.document import Document
from pydantic import BaseModel


class ChatMessage(BaseModel):
    """Represents a chat message within a session."""

    message: str
    message_id: str
    session_id: str


class Doc(BaseModel):
    """Represents a document with content and associated metadata."""

    content: str
    metadata: dict

    def to_langchain_document(self) -> Document:
        """Converts the current Doc instance into a langchain Document."""
        return Document(page_content=self.content, metadata=self.metadata)
