import os
from dataclasses import dataclass, field, is_dataclass
from pathlib import Path

import yaml
from dotenv import load_dotenv
from jinja2 import Template
from langchain.schema.embeddings import Embeddings
from langchain.vectorstores import VectorStore
from langchain_core.language_models import LLM
from langchain_core.language_models.chat_models import BaseChatModel

load_dotenv()


@dataclass
class LLMConfig:
    source: BaseChatModel | LLM | str
    source_config: dict


@dataclass
class VectorStoreConfig:
    source: VectorStore | str
    source_config: dict

    insertion_mode: str  # "None", "full", "incremental"


@dataclass
class EmbeddingModelConfig:
    source: Embeddings | str
    source_config: dict


@dataclass
class DatabaseConfig:
    database_url: str


@dataclass
class RagConfig:
    """
    Configuration class for the Retrieval-Augmented Generation (RAG) system.
    It is meant to be injected in the RAG class to configure the various components.

    This class holds the configuration for the various components that make up the RAG
    system, including the language model, vector store, embedding model, and database
    configurations. It provides a method to construct a RagConfig instance from a YAML
    file, allowing for easy external configuration.

    Attributes:
        llm (LLMConfig): Configuration for the language model component.
        vector_store (VectorStoreConfig): Configuration for the vector store component.
        embedding_model (EmbeddingModelConfig): Configuration for the embedding model
            component.
        database (DatabaseConfig): Configuration for the database connection.

    Methods:
        from_yaml: Class method to create an instance of RagConfig from a YAML file,
            with optional environment variables for template rendering.
    """

    llm: LLMConfig = field(default_factory=LLMConfig)
    vector_store: VectorStoreConfig = field(default_factory=VectorStoreConfig)
    embedding_model: EmbeddingModelConfig = field(default_factory=EmbeddingModelConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    chat_history_window_size: int = 5
    max_tokens_limit: int = 3000
    response_mode: str = None

    @classmethod
    def from_yaml(cls, yaml_path: Path, env: dict = None):
        if env is None:
            env = os.environ
        with Path.open(yaml_path, "r") as file:
            template = Template(file.read())
            config_data = yaml.safe_load(template.render(env))["RagConfig"]

        for field_name, field_type in cls.__annotations__.items():
            if field_name in config_data and is_dataclass(field_type):
                config_data[field_name] = field_type(**config_data[field_name])

        return cls(**config_data)
