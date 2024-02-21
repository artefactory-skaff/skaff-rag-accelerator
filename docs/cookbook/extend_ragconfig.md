As you tune this starter kit to your needs, you may need to add specific configuration that your RAG will use.

For example, let's say you want to add the `foo` configuration parameter to your vector store configuration.

First, add it to `config.py` in the part relavant to the vector store:

```python
# ...

@dataclass
class VectorStoreConfig:
    # ... rest of the VectorStoreConfig ...

    foo: str = "bar"  # We add foo param, of type str, with the default value "bar"

# ...
```

This parameter will now be available in your `RAG` object configuration.

```python
from pathlib import Path
from backend.rag_components.rag import RAG

config_directory = Path("backend/config.yaml")
rag = RAG(config_directory)

print(rag.config.vector_store.foo)
# > bar
```

if you want to override its default value. You can do that in your `config.yaml`:
```yaml
VectorStoreConfig: &VectorStoreConfig
  # ... rest of the VectorStoreConfig ...
  foo: baz
```

```python
print(rag.config.vector_store.foo)
# > baz
```
