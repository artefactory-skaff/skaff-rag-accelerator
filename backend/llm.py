from langchain import chat_models
from pathlib import Path
import yaml

def get_model_instance():
    config = load_models_config()
    llm_spec = getattr(chat_models, config["llm_model_config"]["model_source"])
    all_config_field = {**config["llm_model_config"], **config["llm_provider_config"]}
    kwargs = {key: value for key, value in all_config_field.items() if key in llm_spec.__fields__.keys()}
    return llm_spec(**kwargs)


def load_models_config():
    with open(Path(__file__).parent / "models_config.yaml", "r") as file:
        return yaml.safe_load(file)


