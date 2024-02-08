from pathlib import Path

from fastapi import FastAPI
from langserve import add_routes

from backend.database import Database
from backend.rag_components.rag import RAG


# Initialize the SQL database backing the application
# TODO: documentation link
with Database() as connection:
    connection.initialize_schema()

# Initialize a RAG as discribed in the config.yaml file
# https://artefactory.github.io/skaff-rag-accelerator/rag_object/
rag = RAG(config=Path(__file__).parent / "config.yaml")
chain = rag.get_chain()


# Create a minimal RAG server based on langserve
# Learn how to extend this configuration to add authentication and session management
# https://artefactory.github.io/skaff-rag-accelerator/api_plugins/
app = FastAPI(
    title="RAG Accelerator",
    description="A RAG-based question answering API",
)
add_routes(
    app,
    chain,
)
