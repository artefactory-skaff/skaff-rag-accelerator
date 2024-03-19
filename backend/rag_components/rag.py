from pathlib import Path
from typing import List, Union

from langchain.chat_models.base import BaseChatModel
from langchain.docstore.document import Document
from langchain.indexes import SQLRecordManager, index
from langchain.schema.embeddings import Embeddings
from langchain.vectorstores import VectorStore
from langchain_core.retrievers import BaseRetriever
from langchain.vectorstores.utils import filter_complex_metadata

from backend.config import RagConfig
from backend.database import Database
from backend.logger import get_logger
from backend.rag_components.document_loader import get_documents
from backend.rag_components.embedding import get_embedding_model
from backend.rag_components.llm import get_llm_model
from backend.rag_components.retriever import get_retriever
from backend.rag_components.vector_store import get_vector_store
from backend.rag_components.chain_links.rag_basic import rag_basic
from backend.rag_components.chain_links.rag_with_history import rag_with_history_chain

class RAG:
    """
    The RAG class orchestrates the components necessary for a retrieval-augmented generation pipeline.
    It initializes with a configuration, either directly or from a file.

    The RAG has two main purposes:
        - loading the RAG with documents, which involves ingesting and processing documents to be retrievable by the system
        - generating the chain from the components as specified in the configuration, which entails \
            assembling the various components (language model, embeddings, vector store) into a \
                coherent pipeline for generating responses based on retrieved information.

    Attributes:
        config (RagConfig): Configuration object containing settings for RAG components.
        llm (BaseChatModel): The language model used for generating responses.
        embeddings (Embeddings): The embedding model used for creating vector representations of text.
        vector_store (VectorStore): The vector store that holds and allows for searching of embeddings.
        logger (Logger): Logger for logging information, warnings, and errors.
    """
    def __init__(self, config: Union[Path, RagConfig]):
        if isinstance(config, RagConfig):
            self.config = config
        else:
            self.config = RagConfig.from_yaml(config)

        self.logger = get_logger()
        with Database() as connection:
            connection.run_script(Path(__file__).parent / "rag_tables.sql")

        self.llm: BaseChatModel = get_llm_model(self.config)
        self.embeddings: Embeddings = get_embedding_model(self.config)
        self.vector_store: VectorStore = get_vector_store(self.embeddings, self.config)
        self.retriever: BaseRetriever = get_retriever(self.vector_store)

    def get_chain(self, memory: bool = False):
        if memory:
            chain = rag_with_history_chain(self.config, self.llm, self.retriever)
        else:
            chain = rag_basic(self.llm, self.retriever)
        return chain


    def load_file(self, file_path: Path) -> List[Document]:
        documents = get_documents(file_path, self.llm)
        filtered_documents = filter_complex_metadata(documents)
        return self.load_documents(filtered_documents)

    def load_documents(self, documents: List[Document], insertion_mode: str = None, namespace: str = "default"):
        insertion_mode = insertion_mode or self.config.vector_store.insertion_mode

        record_manager = SQLRecordManager(
            namespace=namespace, db_url=self.config.database.database_url
        )

        record_manager.create_schema()

        self.logger.info(f"Indexing {len(documents)} documents.")

        batch_size = 100
        for batch in range(0, len(documents), batch_size):
            self.logger.info(f"Indexing batch {batch} to {min(len(documents), batch + batch_size)}.")

            indexing_output = index(
                documents[batch : min(len(documents), batch + batch_size)],
                record_manager,
                self.vector_store,
                cleanup=insertion_mode,
                source_id_key="source",
            )
            self.logger.info({"event": "load_documents", **indexing_output})
