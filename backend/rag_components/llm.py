from typing import List
from langchain import chat_models
from langchain.callbacks.base import BaseCallbackHandler


def get_llm_model(config, callbacks: List[BaseCallbackHandler] = []):
    llm_spec = getattr(chat_models, config["llm_model_config"]["model_source"])
    all_config_field = {**config["llm_model_config"], **config["llm_provider_config"]}
    kwargs = {
        key: value for key, value in all_config_field.items() if key in llm_spec.__fields__.keys()
    }
    kwargs["streaming"] = True
    kwargs["callbacks"] = callbacks
    return llm_spec(**kwargs)
