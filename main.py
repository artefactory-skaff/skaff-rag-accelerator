from fastapi import FastAPI, HTTPException, status, Body
from typing import List
from langchain.docstore.document import Document
from document_store import StorageBackend
import document_store
from model import ChatMessage
from model import Doc

app = FastAPI()

@app.post("/index/documents")
async def index_documents(chunks: List[Doc], bucket: str, storage_backend: StorageBackend):
    document_store.store_documents(chunks, bucket, storage_backend)

@app.post("/chat")
async def chat(chat_message: ChatMessage):
    pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)