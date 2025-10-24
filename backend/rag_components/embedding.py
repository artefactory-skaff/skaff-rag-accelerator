# embedding.py
from importlib import import_module

from backend.config import RagConfig

# Example registry mapping provider names to their import paths
EMBEDDING_PROVIDERS = {
    "HuggingFaceEmbeddings": "langchain_huggingface.HuggingFaceEmbeddings",
    "OpenAIEmbeddings": "langchain_openai.OpenAIEmbeddings",
    # Add more providers as needed
}


def get_embedding_model(config: RagConfig):
    source = config.embedding_model.source
    source_config = config.embedding_model.source_config

    # If the source is already an instance, return it directly
    if not isinstance(source, str):
        return source

    # Look up the provider class path
    provider_path = EMBEDDING_PROVIDERS.get(source)
    if not provider_path:
        raise ValueError(f"Unknown embedding provider: {source}")

    module_path, class_name = provider_path.rsplit(".", 1)
    module = import_module(module_path)
    embedding_class = getattr(module, class_name)

    return embedding_class(**source_config)
