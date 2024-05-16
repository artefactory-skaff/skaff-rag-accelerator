"""Quick ad-hoc script that generates markdown documentation for the basic RAG chain and
the RAG chain with memory."""

from pathlib import Path

from backend.rag_components.chain_links.documented_runnable import DocumentedRunnable
from backend.rag_components.rag import RAG

rag = RAG(config=Path(__file__).parents[1] / "backend" / "config.yaml")

chain = rag.get_chain(memory=False)
with (Path(__file__).parent / "backend" / "chains" / "basic_chain.md").open("w") as f:
    f.write(chain.documentation.to_markdown())

chain = rag.get_chain(memory=True)
doc_chain = DocumentedRunnable(
    chain,
    chain_name="RAG with persistant memory",
    user_doc=(
        "This chain answers the provided question based on documents it retreives and "
        "the conversation history. It uses a persistant memory to store the "
        "conversation history."
    ),
)
with (Path(__file__).parent / "backend" / "chains" / "chain_with_memory.md").open(
    "w"
) as f:
    f.write(doc_chain.documentation.to_markdown())
