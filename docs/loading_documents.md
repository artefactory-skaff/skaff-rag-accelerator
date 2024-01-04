## Loading documents

The easiest but least flexible way to load documents to your RAG is to use the `RAG.load_file` method. It will semi-intellignetly try to pick the best Langchain loader and parameters for your file.

```python
from pathlib import Path

from backend.rag_components.rag import RAG


data_directory = Path("data")

config_directory = Path("backend/config.yaml")
rag = RAG(config_directory)

for file in data_directory.iterdir():
    if file.is_file():
        rag.load_file(file)
```

If you want more flexibility, you can use the `rag.load_documents` method which expects a list of `langchain.docstore.document` objects. 

**TODO: example**

## Document indexing

The document loader maintains an index of the loaded documents. You can change it in the configuration of your RAG at `vector_store.insertion_mode` to `None`, `incremental`, or `full`. 

[Details of what that means here.](https://python.langchain.com/docs/modules/data_connection/indexing)