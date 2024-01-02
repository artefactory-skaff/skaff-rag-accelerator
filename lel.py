from pathlib import Path
from backend.rag_components.rag import RAG
from backend.model import Message

config_directory = Path("backend/config.yaml")
rag = RAG(config_directory)

message = Message(
    id="123",
    timestamp="2021-06-01T12:00:00",
    chat_id="123",
    sender="user",
    content="Hello, how are you?",
)
response = rag.generate_response(message)
print(response)