from pathlib import Path

from fastapi import FastAPI
from langserve import add_routes

from backend.api_plugins import (
    authentication_routes,
)
from backend.database import Database
from backend.rag_components.rag import RAG

with Database() as connection:
    connection.initialize_schema()

rag = RAG(config=Path(__file__).parent / "config.yaml")
chain = rag.get_chain(memory=True)
chain.get_graph().print_ascii()

app = FastAPI()
auth = authentication_routes(app)

add_routes(
    app,
    chain,
    dependencies=[auth],
)
