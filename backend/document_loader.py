import inspect
from pathlib import Path
from time import sleep
from typing import List

from langchain.chains import LLMChain
from langchain.chat_models.base import BaseChatModel
from langchain.prompts import PromptTemplate
from langchain.vectorstores import VectorStore
from langchain.vectorstores.utils import filter_complex_metadata


def load_document(file_path: Path, llm: BaseChatModel, vector_store: VectorStore):
    documents = get_documents(file_path, llm)
    filtered_documents = filter_complex_metadata(documents)
    vector_store.add_documents(documents)


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
    from backend.document_loader import get_documents
    from backend.rag_components.embedding import get_embedding_model
    from backend.rag_components.llm import get_llm_model
    from backend.rag_components.vector_store import get_vector_store

    config = get_config()
    llm = get_llm_model(config)
    embeddings = get_embedding_model(config)
    vector_store = get_vector_store(embeddings)

    document = load_document(
        file_path=Path(
            "/Users/alexis.vialaret/vscode_projects/skaff-rag-accelerator/data/billionaires_csv.csv"
        ),
        llm=llm,
        vector_store=vector_store,
    )
    print(document)
