import chromadb
from storage_backend import StorageBackend, get_storage_root_path

root_path = get_storage_root_path("sample_bucket", StorageBackend.GCS)
client = chromadb.PersistentClient(root_path / "chromadb")
collection = client.get_or_create_collection("embeddings")
