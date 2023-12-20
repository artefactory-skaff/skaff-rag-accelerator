import inspect

from langchain import vectorstores


def get_vector_store(embedding_model, config):
    vector_store_spec = getattr(vectorstores, config["vector_store_provider"]["model_source"])
    all_config_field = config["vector_store_provider"]

    # the vector store class in langchain doesn't have a uniform interface to pass the embedding model
    # we extract the propertiy of the class that matches the 'Embeddings' type
    # and instanciate the vector store with our embedding model
    signature = inspect.signature(vector_store_spec.__init__)
    parameters = signature.parameters
    params_dict = dict(parameters)
    embedding_param = next(
        (param for param in params_dict.values() if "Embeddings" in str(param.annotation)), None
    )

    kwargs = {key: value for key, value in all_config_field.items() if key in parameters.keys()}
    kwargs[embedding_param.name] = embedding_model
    vector_store = vector_store_spec(**kwargs)
    return vector_store
