from langchain.docstore.document import Document
from enum import Enum
from typing_extensions import List
from langchain.vectorstores import Chroma
import chromadb
from langchain.embeddings import OpenAIEmbeddings


class StorageBackend(Enum):
    LOCAL = "local"
    MEMORY = "memory"
    GCS = "gcs"
    S3 = "s3"
    AZURE = "az"


def get_storage_root_path(bucket_name, storage_backend: StorageBackend):
    root_path = Path(f"{storage_backend.value}://{bucket_name}")
    return root_path

def persist_to_bucket(bucket_path: str, store: Chroma):
    store.persist('./db/chroma')
    #TODO: Uplaod persisted file on disk to gcs


def store_documents(docs: List[Document], bucket_path: str, storage_backend: StorageBackend):
    lagnchain_documents = [doc.to_langchain_document() for doc in docs]
    embeddings_model = OpenAIEmbeddings()
    persistent_client = chromadb.PersistentClient()
    collection = persistent_client.get_or_create_collection(get_storage_root_path(bucket_path, storage_backend))
    collection.add(documents=lagnchain_documents)
    langchain_chroma = Chroma(
        client=persistent_client,
        collection_name=bucket_path,
        embedding_function=embeddings_model.embed_documents,
    )
    print("There are", langchain_chroma._collection.count(), "in the collection")








