from upath import UPath as Path
from enum import Enum


class StorageBackend(Enum):
    LOCAL = "local"
    MEMORY = "memory"
    GCS = "gcs"
    S3 = "s3"
    AZURE = "az"


def get_storage_root_path(bucket_name, storage_backend: StorageBackend):
    root_path = Path(f"{storage_backend.value}://{bucket_name}")
    return root_path
