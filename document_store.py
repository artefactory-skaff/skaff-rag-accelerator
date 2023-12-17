from enum import Enum
from pathlib import Path
from typing import List

import chromadb
from langchain.docstore.document import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma


class StorageBackend(Enum):
    """Enumeration of supported storage backends."""

    LOCAL = "local"
    MEMORY = "memory"
    GCS = "gcs"
    S3 = "s3"
    AZURE = "az"


def get_storage_root_path(bucket_name: str, storage_backend: StorageBackend) -> Path:
    """Constructs the root path for the storage based on the bucket name and storage backend."""
    return Path(f"{storage_backend.value}://{bucket_name}")


def persist_to_bucket(bucket_path: str, store: Chroma) -> None:
    """Persists the data in the given Chroma store to a bucket."""
    store.persist("./db/chroma")
    # TODO: Uplaod persisted file on disk to bucket_path gcs


def store_documents(
    docs: List[Document], bucket_path: str, storage_backend: StorageBackend
) -> None:
    """Stores a list of documents in a specified bucket using a given storage backend."""
    langchain_documents = [doc.to_langchain_document() for doc in docs]
    embeddings_model = OpenAIEmbeddings()
    persistent_client = chromadb.PersistentClient()
    collection = persistent_client.get_or_create_collection(
        get_storage_root_path(bucket_path, storage_backend)
    )
    collection.add(documents=langchain_documents)
    langchain_chroma = Chroma(
        client=persistent_client,
        collection_name=bucket_path,
        embedding_function=embeddings_model.embed_documents,
    )
    print("There are", langchain_chroma._collection.count(), "in the collection")
