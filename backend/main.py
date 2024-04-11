from pathlib import Path

from fastapi import FastAPI
from langserve import add_routes

from backend.api_plugins import authentication_routes, session_routes
from backend.rag_components.rag import RAG
from backend import ENABLE_AUTHENTICATION

# Initialize a RAG as discribed in the config.yaml file
# https://artefactory.github.io/skaff-rag-accelerator/backend/rag_ragconfig/
rag = RAG(config=Path(__file__).parent / "config.yaml")

if ENABLE_AUTHENTICATION:
    chain = rag.get_chain(memory=True)
else:
    chain = rag.get_chain(memory=False)


# Create a minimal RAG server based on langserve
# Learn how to extend this configuration to add authentication and session management
# https://artefactory.github.io/skaff-rag-accelerator/backend/plugins/plugins/
app = FastAPI(
    title="RAG Accelerator",
    description="A RAG-based question answering API",
)

if ENABLE_AUTHENTICATION:
    # Add authentication and session management to the app
    auth = authentication_routes(app)
    session_routes(app, authentication=auth)
    dependencies = [auth]
else:
    dependencies = None

add_routes(app, chain, dependencies=dependencies)
