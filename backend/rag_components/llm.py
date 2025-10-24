from importlib import import_module
from typing import List

from langchain.callbacks.base import BaseCallbackHandler

# Example registry mapping provider names to their import paths
LLM_PROVIDERS = {
    "AzureChatOpenAI": "langchain_openai.AzureChatOpenAI",
    "ChatHuggingFace": "langchain_hugginface.ChatHuggingFace",
    # Add more providers as needed
}


def get_llm_model(config, callbacks: List[BaseCallbackHandler] = []):
    source = config.llm.source
    source_config = config.llm.source_config

    # If already an instance, return directly
    if not isinstance(source, str):
        return source

    # Look up the provider class path
    provider_path = LLM_PROVIDERS.get(source)
    if not provider_path:
        raise ValueError(f"Unknown LLM provider: {source}")

    module_path, class_name = provider_path.rsplit(".", 1)
    module = import_module(module_path)
    llm_class = getattr(module, class_name)

    # Prepare kwargs, add streaming and callbacks
    kwargs = {k: v for k, v in source_config.items()}
    kwargs["streaming"] = True
    kwargs["callbacks"] = callbacks

    return llm_class(**kwargs)
