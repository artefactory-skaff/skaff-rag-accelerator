from langchain_community import embeddings

from backend.config import RagConfig


def get_embedding_model(config: RagConfig):
    spec = getattr(embeddings, config.embedding_model.source)
    kwargs = {
        key: value for key, value in config.embedding_model.source_config.items() if key in spec.__fields__.keys()
    }
    return spec(**kwargs)
