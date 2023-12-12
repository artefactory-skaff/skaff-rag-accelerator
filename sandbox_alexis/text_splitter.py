from typing import Optional

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader
from langchain.schema.document import Document


def load_and_split_document(
    file_path: Optional[str] = None,
    text: Optional[str] = None,
    chunk_size: Optional[int] = 5000,
    chunk_overlap: Optional[int] = 50,
) -> list[Document]:
    if file_path and text:
        raise ValueError("Only one of `file_path` or `text` should be provided.")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )

    if file_path:
        loader = TextLoader(file_path=file_path)
        doc = loader.load()

    if text:
        doc = [Document(page_content=text)]

    chunks = text_splitter.split_documents(doc)
    return chunks