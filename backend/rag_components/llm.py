from langchain import chat_models


def get_llm_model(config):
    llm_spec = getattr(chat_models, config["llm_model_config"]["model_source"])
    all_config_field = {**config["llm_model_config"], **config["llm_provider_config"]}
    kwargs = {
        key: value for key, value in all_config_field.items() if key in llm_spec.__fields__.keys()
    }
    return llm_spec(**kwargs)
