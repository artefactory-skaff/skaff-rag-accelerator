from logging import Logger
import os
from pathlib import Path
from typing import List, Union


from langchain.docstore.document import Document
from langchain.vectorstores.utils import filter_complex_metadata
from langchain.callbacks import AsyncIteratorCallbackHandler
from backend.rag_components.chain import get_answer_chain, get_response_stream
from langchain.indexes import SQLRecordManager, index
from langchain.chat_models.base import BaseChatModel
from langchain.vectorstores import VectorStore
from langchain.schema.embeddings import Embeddings


from backend.config import RagConfig
from backend.model import Message
from backend.rag_components.chat_message_history import get_conversation_buffer_memory
from backend.rag_components.document_loader import get_documents
from backend.rag_components.embedding import get_embedding_model
from backend.rag_components.llm import get_llm_model
from backend.rag_components.logging_callback_handler import LoggingCallbackHandler
from backend.rag_components.vector_store import get_vector_store


class RAG:
    def __init__(self, config: Union[Path, RagConfig], logger: Logger = None, context: dict = None):
        if isinstance(config, RagConfig):
            self.config = config
        else:
            self.config = RagConfig.from_yaml(config)

        self.logger = logger
        self.context = context

        self.llm: BaseChatModel = get_llm_model(self.config)
        self.embeddings: Embeddings = get_embedding_model(self.config)
        self.vector_store: VectorStore = get_vector_store(self.embeddings, self.config)

    def generate_response(self, message: Message):
        memory = get_conversation_buffer_memory(self.config, message.chat_id)
        streaming_callback_handler = AsyncIteratorCallbackHandler()
        logging_callback_handler = LoggingCallbackHandler(self.logger, context=self.context)
        answer_chain = get_answer_chain(self.config, self.vector_store, memory, streaming_callback_handler=streaming_callback_handler, logging_callback_handler=logging_callback_handler)
        response_stream = get_response_stream(answer_chain, message.content, streaming_callback_handler)
        return response_stream
    
    def load_file(self, file_path: Path) -> List[Document]:
        documents = get_documents(file_path, self.llm)
        filtered_documents = filter_complex_metadata(documents)
        return self.load_documents(filtered_documents)

    def load_documents(self, documents: List[Document]):
        record_manager = SQLRecordManager(
            namespace="vector_store/my_docs", db_url=self.config.database.database_url
        )
        record_manager.create_schema()
        indexing_output = index(
            documents,
            record_manager,
            self.vector_store,
            cleanup=self.config.vector_store_config.insertion_mode,
            source_id_key="source",
        )
        self.logger.info({"event": "load_documents", **indexing_output})


if __name__ == "__main__":
    file_path = Path(__file__).parent.parent.parent / "data"
    rag = RAG()
    for file in file_path.iterdir():
        if file.is_file():
            rag.load_file(file)
