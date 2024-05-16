from pathlib import Path

from fastapi import FastAPI
from langserve import add_routes

# from backend.api_plugins import authentication_routes, session_routes
from backend.rag_components.rag import RAG

# Initialize a RAG as discribed in the config.yaml file
# https://artefactory-skaff.github.io/skaff-rag-accelerator/backend/rag_ragconfig/
rag = RAG(config=Path(__file__).parent / "config.yaml")
chain = rag.get_chain()

# Create a minimal RAG server based on langserve
# Learn how to extend this configuration to add authentication and session management
# https://artefactory-skaff.github.io/skaff-rag-accelerator/backend/plugins/plugins/
app = FastAPI(
    title="RAG Accelerator",
    description="A RAG-based question answering API",
)
add_routes(app, chain)
