from pathlib import Path
from typing import List

from langchain.docstore.document import Document
from langchain.vectorstores import VectorStore
from langchain.vectorstores.utils import filter_complex_metadata
from backend.rag_components.chain import get_answer_chain, get_response_stream

from backend.rag_components.config_renderer import get_config
from backend.model import Message
from backend.rag_components.chat_message_history import get_conversation_buffer_memory
from backend.rag_components.document_loader import get_documents
from backend.rag_components.embedding import get_embedding_model
from backend.rag_components.llm import get_llm_model
from backend.rag_components.vector_store import get_vector_store


class RAG:
    def __init__(self, config_file_path: Path = None):
        if config_file_path is None:
            config_file_path = Path(__file__).parents[1]

        self.config = get_config(config_file_path)
        self.llm = get_llm_model(self.config)
        self.embeddings = get_embedding_model(self.config)
        self.vector_store: VectorStore = get_vector_store(self.embeddings, self.config)

    def generate_response(self, message: Message):
        memory = get_conversation_buffer_memory(self.config, message.chat_id)
        answer_chain, callback_handler = get_answer_chain(self.config, self.vector_store, memory)
        response_stream = get_response_stream(answer_chain, callback_handler, message.content)
        return response_stream

    def load_documents(self, documents: List[Document]):
        # TODO améliorer la robustesse du load_document
        # TODO agent langchain qui fait le get_best_loader
        self.vector_store.add_documents(documents)

    def load_file(self, file_path: Path):
        documents = get_documents(file_path, self.llm)
        filtered_documents = filter_complex_metadata(documents)
        self.vector_store.add_documents(filtered_documents)

    # TODO pour chaque fichier -> stocker un hash en base
    # TODO avant de loader un fichier dans le vector store si le hash est dans notre db est append le doc dans le vector store que si le hash est inexistant
    # TODO éviter de dupliquer les embeddings

    def serve():
        pass


if __name__ == "__main__":
    file_path = Path(__file__).parent.parent.parent / "data"
    rag = RAG()
    for file in file_path.iterdir():
        if file.is_file():
            rag.load_file(file)
