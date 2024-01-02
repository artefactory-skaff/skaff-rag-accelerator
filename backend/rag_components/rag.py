import asyncio
from logging import Logger
from pathlib import Path
from typing import AsyncIterator, List, Union


from langchain.docstore.document import Document
from langchain.vectorstores.utils import filter_complex_metadata
from langchain.callbacks import AsyncIteratorCallbackHandler
from backend.rag_components.chain import get_answer_chain, async_get_response, stream_get_response
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
from backend.rag_components.streaming_callback_handler import StreamingCallbackHandler
from backend.rag_components.vector_store import get_vector_store


class RAG:
    def __init__(self, config: Union[Path, RagConfig], logger: Logger = None, context: dict = {}):
        if isinstance(config, RagConfig):
            self.config = config
        else:
            self.config = RagConfig.from_yaml(config)

        self.logger = logger or Logger("RAG")
        self.context = context

        self.llm: BaseChatModel = get_llm_model(self.config)
        self.embeddings: Embeddings = get_embedding_model(self.config)
        self.vector_store: VectorStore = get_vector_store(self.embeddings, self.config)

    def generate_response(self, message: Message) -> str:
        loop = asyncio.get_event_loop()
        response_stream = self.async_generate_response(message)
        responses = loop.run_until_complete(self._collect_responses(response_stream))
        return "".join([str(response) for response in responses])
    
    def stream_generate_response(self, message: Message) -> AsyncIterator[str]:
        memory = get_conversation_buffer_memory(self.config, message.chat_id)
        streaming_callback_handler = StreamingCallbackHandler()
        logging_callback_handler = LoggingCallbackHandler(self.logger, context=self.context)
        answer_chain = get_answer_chain(self.config, self.vector_store, memory, streaming_callback_handler=streaming_callback_handler, logging_callback_handler=logging_callback_handler)
        response_stream = stream_get_response(answer_chain, message.content, streaming_callback_handler)
        return response_stream
    
    def async_generate_response(self, message: Message) -> AsyncIterator[str]:
        memory = get_conversation_buffer_memory(self.config, message.chat_id)
        streaming_callback_handler = AsyncIteratorCallbackHandler()
        logging_callback_handler = LoggingCallbackHandler(self.logger, context=self.context)
        answer_chain = get_answer_chain(self.config, self.vector_store, memory, streaming_callback_handler=streaming_callback_handler, logging_callback_handler=logging_callback_handler)
        response_stream = async_get_response(answer_chain, message.content, streaming_callback_handler)
        return response_stream
    
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

    async def _collect_responses(self, response_stream):
        responses = []
        async for response in response_stream:
            responses.append(response)
        return responses
