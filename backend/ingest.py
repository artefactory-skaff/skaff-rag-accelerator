"""Ingest PDF files into the vectorstore for RAG Option 2."""

import logging
from pathlib import Path

from tqdm.auto import tqdm
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.config import RagConfig
from backend.rag_components.rag import RAG

logger = logging.getLogger(__name__)


def ingest_pdf(file_path: str | Path) -> None:
    """Ingest a PDF file.

    Args:
        file_path (str | Path): Path to the PDF file.
    """
    logger.info(f"Processing {file_path}")

    # Load PDF
    loader = PyPDFLoader(file_path)
    pages = loader.load_and_split()

    # Split document
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200, add_start_index=True)
    all_splits = text_splitter.split_documents(pages)

    # Load RAG
    rag_config = RagConfig.from_yaml(Path("backend", "config.yaml"))
    rag_config.database.database_url = "sqlite:///database/rag.sqlite3"

    rag = RAG(config=rag_config)

    print("LLM:", rag.llm.__class__.__name__)
    print("Embedding model:", rag.embeddings.__class__.__name__)
    print("Vector store:", rag.vector_store.__class__.__name__)
    print("Retriever:", rag.retriever.__class__.__name__)

    # Add chunks to vectorstore
    logger.info("Adding texts to vectorstore")
    rag.load_documents(all_splits)

    return


def main() -> None:
    """Ingest all PDF files in the data folder."""

    docs_folder = Path("data/")

    for file_path in tqdm(sorted(docs_folder.glob("**/*.pdf"))):
        ingest_pdf(file_path)

    logger.info("Finished processing all PDF files")


if __name__ == "__main__":
    main()
