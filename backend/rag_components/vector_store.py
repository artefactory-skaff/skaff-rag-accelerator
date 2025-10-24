import inspect
from importlib import import_module

from backend.config import RagConfig

# vectorstore_registry.py
VECTOR_STORE_PROVIDERS = {
    "Chroma": "langchain_chroma.Chroma",
    "FAISS": "langchain_community.vectorstores.FAISS",
    "PineconeVectorStore": "langchain_pinecone.PineconeVectorStore",
    # Ajoute d'autres providers ici si besoin
}


def get_vector_store(embedding_model, config: RagConfig):
    source = config.vector_store.source
    source_config = config.vector_store.source_config

    # Si c’est déjà une instance, on la retourne
    if not isinstance(source, str):
        return source

    # Lookup du chemin de la classe
    provider_path = VECTOR_STORE_PROVIDERS.get(source)
    if not provider_path:
        raise ValueError(f"Unknown vector store provider: {source}")

    module_path, class_name = provider_path.rsplit(".", 1)
    module = import_module(module_path)
    vector_store_class = getattr(module, class_name)

    # Détection du paramètre d’embedding
    signature = inspect.signature(vector_store_class.__init__)
    embedding_param = next(
        (p for p in signature.parameters.values() if "Embeddings" in str(p.annotation)),
        None,
    )
    if not embedding_param:
        raise ValueError(f"No embedding parameter found in {vector_store_class}")

    # Préparation des kwargs
    kwargs = {k: v for k, v in source_config.items() if k in signature.parameters}
    kwargs[embedding_param.name] = embedding_model

    return vector_store_class(**kwargs)
