import inspect
from langchain_community import vectorstores
from backend.config import RagConfig


def get_vector_store(embedding_model, config: RagConfig):
    vector_store_spec = getattr(vectorstores, config.vector_store.source)

    # the vector store class in langchain doesn't have a uniform interface to pass the embedding model
    # we extract the propertiy of the class that matches the 'Embeddings' type
    # and instanciate the vector store with our embedding model
    signature = inspect.signature(vector_store_spec.__init__)
    parameters = signature.parameters
    params_dict = dict(parameters)
    embedding_param = next(
        (param for param in params_dict.values() if "Embeddings" in str(param.annotation)), None
    )

    kwargs = {key: value for key, value in config.vector_store.source_config.items() if key in parameters.keys()}
    kwargs[embedding_param.name] = embedding_model

    if config.vector_store.source == "MatchingEngine":
        import os
        from google.cloud import storage
        from google.cloud import aiplatform
        aiplatform.init(project=os.environ.get("PROJECT_ID"), location=os.environ.get("REGION"))
        kwargs["gcs_client"] = storage.Client(project=os.environ.get("PROJECT_ID"))
        kwargs["index"] = aiplatform.MatchingEngineIndex(index_name=os.environ.get("INDEX_ID"))
        kwargs["endpoint"] = aiplatform.MatchingEngineIndexEndpoint(index_endpoint_name=os.environ.get("ENDPOINT_ID"))

    vector_store = vector_store_spec(**kwargs)
    return vector_store
