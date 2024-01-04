It provides a unique interface to the RAG's functionalities. 

## Using the `RAG` class directly:
```python
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
```

## Usage in the API

Out of the box, A RAG object is created from your configuration and used by the `/chat/{chat_id}/user_message` endpoint in [`backend/main.py`](backend/main.py)

The RAG class initializes key components (language model, embeddings, vector store), and generates responses to user messages using an answer chain.

It also manages document loading and indexing based on configuration settings.


