import inspect
from pathlib import Path
from typing import List, Union

from langchain.chains import LLMChain
from langchain.chat_models.base import BaseChatModel
from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate
from langchain.vectorstores import VectorStore
from langchain.vectorstores.utils import filter_complex_metadata

from backend.chatbot import get_answer_chain, get_response
from backend.rag_components.chat_message_history import get_conversation_buffer_memory
from backend.rag_components.embedding import get_embedding_model
from backend.rag_components.llm import get_llm_model
from backend.rag_components.vector_store import get_vector_store


def generate_response(file_path: Path, config, input_query):
    llm = get_llm_model(config)
    embeddings = get_embedding_model(config)
    vector_store = get_vector_store(embeddings, config)
    store_documents(file_path, llm, vector_store)
    memory = get_conversation_buffer_memory(config, input_query.chat_id)
    answer_chain = get_answer_chain(llm, vector_store, memory)
    response = get_response(answer_chain, input_query.content)
    return response


def store_documents(
    data_to_store: Union[Path, Document], llm: BaseChatModel, vector_store: VectorStore
):
    if isinstance(data_to_store, Path):
        documents = get_documents(data_to_store, llm)
        filtered_documents = filter_complex_metadata(documents)
        vector_store.add_documents(filtered_documents)
    else:
        vector_store.add_documents(data_to_store)


def get_documents(file_path: Path, llm: BaseChatModel):
    file_extension = file_path.suffix
    loader_class_name = get_best_loader(file_extension, llm)

    if loader_class_name == "None":
        raise Exception(f"No loader found for {file_extension} files.")

    loader_class = get_loader_class(loader_class_name)
    loader = loader_class(str(file_path))
    return loader.load()


def get_loader_class(loader_class_name: str):
    import langchain.document_loaders

    loader_class = getattr(langchain.document_loaders, loader_class_name)
    return loader_class


def get_best_loader(file_extension: str, llm: BaseChatModel):
    loaders = get_loaders()
    prompt = PromptTemplate(
        input_variables=["file_extension", "loaders"],
        template="""
    Among the following loaders, which is the best to load a "{file_extension}" file? Only give me one the class name without any other special characters. If no relevant loader is found, respond "None".

    Loaders: {loaders}
    """,
    )
    chain = LLMChain(llm=llm, prompt=prompt, output_key="loader_class_name")

    return chain({"file_extension": file_extension, "loaders": loaders})["loader_class_name"]


def get_loaders() -> List[str]:
    import langchain.document_loaders

    loaders = []
    for _, obj in inspect.getmembers(langchain.document_loaders):
        if inspect.isclass(obj):
            loaders.append(obj.__name__)
    return loaders


if __name__ == "__main__":
    from pathlib import Path

    from backend.config_renderer import get_config
    from frontend.lib.chat import Message

    config = get_config()
    data_to_store = Path(f"{Path(__file__).parent.parent.parent}/data/billionaires_csv.csv")
    prompt = "Quelles sont les 5 plus grandes fortunes de France ?"
    chat_id = "test"
    input_query = Message("user", prompt, chat_id)
    response = generate_response(data_to_store, config, input_query)
    print(response)
