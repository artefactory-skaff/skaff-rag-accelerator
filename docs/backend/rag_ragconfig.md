## The `RAG` class

The RAG class orchestrates the components necessary for a retrieval-augmented generation pipeline.
It initializes with a configuration, either directly or from a file.

![RAG](RAG.png)

The RAG object has two main purposes:

- loading the RAG with documents, which involves ingesting and processing documents to be retrievable by the system
- generating the chain from the components as specified in the configuration, which entails assembling the various components (language model, embeddings, vector store) into a coherent pipeline for generating responses based on retrieved information.


!!! example "Loading and querying documents"
    ```python
    from pathlib import Path
    from backend.rag_components.rag import RAG

    rag = RAG(config=Path(__file__).parent / "backend" / "config.yaml")
    chain = rag.get_chain()

    print(chain.invoke("Who is bill Gates?"))
    # > content='Documents have not been provided, and thus I am unable to give a response based on them. Would you like me to answer based on general knowledge instead?'

    rag.load_file(Path(__file__).parent / "data_sample" / "billionaires.csv")
    # > loader selected CSVLoader for /.../data_sample/billionaires.csv
    # > {'event': 'load_documents', 'num_added': 2640, 'num_updated': 0, 'num_skipped': 0, 'num_deleted': 0}

    print(chain.invoke("Who is bill Gates?"))
    # > content='Bill Gates is a 67-year-old businessman from the United States, residing in Medina, Washington. He is the co-chair of the Bill & Melinda Gates Foundation and is recognized for his self-made success, primarily through Microsoft in the technology industry. As of the provided document dated April 4, 2023, Bill Gates has a final worth of $104 billion, ranking him 6th in the category of Technology. His full name is William Gates, and he was born on October 28, 1955.'
    ```

## `RAGConfig`

Configuration of the RAG is done using the `RAGConfig` dataclass. You can instanciate one directly in python, but the preferred way is to use the `backend/config.yaml` file. This YAML is then automatically parsed into a `RAGConfig` that can be fed to the `RAG` class.

The configuration provides you with a way to input which implementation you want to use for each RAG components:

- The LLM
- The embedding model
- The vector store / retreiver
- The memory / database

Zooming in on the `LLMConfig` as an example:
```python
@dataclass
class LLMConfig:
    source: BaseChatModel | LLM | str
    source_config: dict
    temperature: float
```

- `source` is the name of name of the langchain class name of your model, either a `BaseChatModel` or `LLM`.
- `source_config` is are the parameters used to instanciate the `source`.
- `temperature` regulates the unpredictability of a language model's output.

Example of a configuration that uses a local model served with Ollama. In `backend/config.yaml`:
```yaml
LLMConfig: &LLMConfig
  source: ChatOllama
  source_config:
    model: tinyllama
    temperature: 0
```

!!! info "Configuration recipes"
    You can find fully tested recipes for LLMConfig, VectorStoreConfig, EmbeddingModelConfig, and DatabaseConfig [in the Cookbook](../cookbook/cookbook.md).

This is the python equivalent that is generated and executed under the hood when a `RAG` object is created.
```python
llm = ChatOllama(model="tinyllama", temperature=0)
```


You can also write the configurations directly in python, although that's not the recommended approach here.
```python
from langchain_community.chat_models import ChatOllama

from backend.config import LLMConfig

llm_config = LLMConfig(
    source=ChatOllama,
    source_config={"model": "llama2", "temperature": 0},
)
```

### Extending the `RAGConfig`

See: [How to extend the RAGConfig](../cookbook/extend_ragconfig.md)
