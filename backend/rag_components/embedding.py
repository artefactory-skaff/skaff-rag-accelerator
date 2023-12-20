from langchain import embeddings


def get_embedding_model(config):
    spec = getattr(embeddings, config["embedding_model_config"]["model_source"])
    all_config_field = {**config["embedding_model_config"], **config["embedding_provider_config"]}
    kwargs = {
        key: value
        for key, value in all_config_field.items()
        if key in spec.__fields__.keys()
    }
    return spec(**kwargs)
