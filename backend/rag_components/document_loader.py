import inspect
from pathlib import Path
from typing import List

from langchain.chains import LLMChain
from langchain.chat_models.base import BaseChatModel
from langchain.prompts import PromptTemplate


def get_documents(file_path: Path, llm: BaseChatModel):
    file_extension = file_path.suffix
    loader_class_name = get_best_loader(file_extension, llm)
    print(f"loader selected {loader_class_name} for {file_path}")

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
    Among the following loaders, which is the best to load a "{file_extension}" file? \
        Only give me one the class name without any other special characters. If no relevant loader is found, respond "None".

    Loaders: {loaders}
    """,
    )
    chain = LLMChain(llm=llm, prompt=prompt, output_key="loader_class_name")

    return chain({"file_extension": file_extension, "loaders": loaders})["loader_class_name"]


def get_loaders() -> List[str]:
    import langchain_community.document_loaders

    loaders = []
    for _, obj in inspect.getmembers(langchain_community.document_loaders):
        if inspect.isclass(obj):
            loaders.append(obj.__name__)
    return loaders
