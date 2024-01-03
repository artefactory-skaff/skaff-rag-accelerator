from typing import List
from langchain import chat_models
from langchain.callbacks.base import BaseCallbackHandler

from backend.config import RagConfig


def get_llm_model(config: RagConfig, callbacks: List[BaseCallbackHandler] = []):
    llm_spec = getattr(chat_models, config.llm.source)
    kwargs = {
        key: value for key, value in config.llm.source_config.items() if key in llm_spec.__fields__.keys()
    }
    kwargs["streaming"] = True
    kwargs["callbacks"] = callbacks

    return llm_spec(**kwargs)
