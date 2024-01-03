from dataclasses import dataclass, field, is_dataclass
import os
from pathlib import Path
from dotenv import load_dotenv
from jinja2 import Template

from langchain.chat_models.base import BaseChatModel
from langchain.vectorstores import VectorStore
from langchain.schema.embeddings import Embeddings
import yaml

load_dotenv()

@dataclass
class LLMConfig:
    source: BaseChatModel | str = "AzureChatOpenAI"
    source_config: dict = field(default_factory=lambda: {
        "openai_api_type": "azure",
        "openai_api_base": "https://poc-genai-gpt4.openai.azure.com/",
        "openai_api_version": "2023-07-01-preview",
        "openai_api_key": os.environ.get("OPENAI_API_KEY"),
        "deployment_name": "gpt4v",
    })

    temperature: float = 0.1

@dataclass
class VectorStoreConfig:
    source: VectorStore | str = "Chroma"
    source_config: dict = field(default_factory=lambda: {
        "persist_directory": "vector_database/", 
        "collection_metadata": {
            "hnsw:space": "cosine"
        }
    })

    retreiver_search_type: str = "similarity"
    retreiver_config: dict = field(default_factory=lambda: {
        "top_k": 20, 
        "score_threshold": 0.5
    })

    insertion_mode: str = "full"  # "None", "full", "incremental"

@dataclass
class EmbeddingModelConfig:
    source: Embeddings | str = "OpenAIEmbeddings"
    source_config: dict = field(default_factory=lambda: {
        "openai_api_type": "azure",
        "openai_api_base": "https://poc-openai-artefact.openai.azure.com/",
        "openai_api_key": os.environ.get("EMBEDDING_API_KEY"),
        "deployment": "embeddings",
        "chunk_size": 500,
    })

@dataclass
class DatabaseConfig:
    database_url: str = os.environ.get("DATABASE_URL")

@dataclass
class RagConfig:
    llm:                      LLMConfig             = field(default_factory=LLMConfig)
    vector_store:             VectorStoreConfig     = field(default_factory=VectorStoreConfig)
    embedding_model:          EmbeddingModelConfig  = field(default_factory=EmbeddingModelConfig)
    database:                 DatabaseConfig        = field(default_factory=DatabaseConfig)
    chat_history_window_size: int                   = 5
    max_tokens_limit:         int                   = 3000
    response_mode:            str                   = "normal"

    @classmethod
    def from_yaml(cls, yaml_path: Path, env: dict = None):
        if env is None:
            env = os.environ
        with open(yaml_path, "r") as file:
            template = Template(file.read())
            config_data = yaml.safe_load(template.render(env))["RagConfig"]

        for field_name, field_type in cls.__annotations__.items():
            if field_name in config_data and is_dataclass(field_type):
                config_data[field_name] = field_type(**config_data[field_name])

        return cls(**config_data)
