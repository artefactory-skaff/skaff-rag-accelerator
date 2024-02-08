from pathlib import Path
from typing import List, Union

from langchain.chat_models.base import BaseChatModel
from langchain.docstore.document import Document
from langchain.indexes import SQLRecordManager, index
from langchain.schema.embeddings import Embeddings
from langchain.vectorstores import VectorStore
from langchain.vectorstores.utils import filter_complex_metadata

from backend.config import RagConfig
from backend.rag_components.chain import get_base_chain, get_memory_chain
from backend.rag_components.document_loader import get_documents
from backend.rag_components.embedding import get_embedding_model
from backend.rag_components.llm import get_llm_model
from backend.rag_components.vector_store import get_vector_store


class RAG:
    def __init__(self, config: Union[Path, RagConfig]):
        if isinstance(config, RagConfig):
            self.config = config
        else:
            self.config = RagConfig.from_yaml(config)

        self.llm: BaseChatModel = get_llm_model(self.config)
        self.embeddings: Embeddings = get_embedding_model(self.config)
        self.vector_store: VectorStore = get_vector_store(self.embeddings, self.config)

    def get_chain(self, memory: bool = False):
        if memory:
            chain = get_memory_chain(self.config, self.vector_store)
        else:
            chain = get_base_chain(self.config, self.vector_store)
        return chain


    def load_file(self, file_path: Path) -> List[Document]:
        documents = get_documents(file_path, self.llm)
        filtered_documents = filter_complex_metadata(documents)
        return self.load_documents(filtered_documents)

    def load_documents(self, documents: List[Document], insertion_mode: str = None):
        insertion_mode = insertion_mode or self.config.vector_store.insertion_mode

        record_manager = SQLRecordManager(
            namespace="vector_store/my_docs", db_url=self.config.database.database_url
        )
        record_manager.create_schema()
        indexing_output = index(
            documents,
            record_manager,
            self.vector_store,
            cleanup=insertion_mode,
            source_id_key="source",
        )
        self.logger.info({"event": "load_documents", **indexing_output})
