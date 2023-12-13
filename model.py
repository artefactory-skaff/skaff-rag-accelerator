from pydantic import BaseModel
from langchain.docstore.document import Document

class ChatMessage(BaseModel):
    message: str
    message_id: str
    session_id: str

class Doc(BaseModel):
    content: str
    metadata: dict

    def to_langchain_document():
        return Document(page_content=self.content, metadata=self.metadata)