from langchain import chat_models
from langchain.callbacks import AsyncIteratorCallbackHandler


def get_llm_model(config, streaming=False):
    llm_spec = getattr(chat_models, config["llm_model_config"]["model_source"])
    all_config_field = {**config["llm_model_config"], **config["llm_provider_config"]}
    kwargs = {
        key: value for key, value in all_config_field.items() if key in llm_spec.__fields__.keys()
    }
    if streaming:
        kwargs["streaming"] = streaming
        callback_handler = AsyncIteratorCallbackHandler()
        kwargs["callbacks"] = [callback_handler]
        return llm_spec(**kwargs), callback_handler
    else:
        return llm_spec(**kwargs)