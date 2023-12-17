from typing import List, Optional

from langchain.document_loaders import TextLoader
from langchain.schema.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter


def load_and_split_document(
    file_path: Optional[str] = None,
    text: Optional[str] = None,
    chunk_size: Optional[int] = 5000,
    chunk_overlap: Optional[int] = 50,
) -> List[Document]:
    """Loads a document from a file or text and splits it into chunks."""
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

    return text_splitter.split_documents(doc)
