## Chroma

```yaml
VectorStoreConfig: &VectorStoreConfig
  source: Chroma
  source_config:
    persist_directory: vector_database/
    collection_metadata:
      hnsw:space: cosine

  retreiver_search_type: similarity
  retreiver_config:
    top_k: 20
    score_threshold: 0.5

  insertion_mode: full
```

`persist_directory`: where, locally the Chroma database will be persisted.

`hnsw:space: cosine`: [distance function used. Default is `l2`.](https://docs.trychroma.com/usage-guide#changing-the-distance-function) Cosine is bounded [0; 1], making it easier to set a score threshold for retrival.

`top_k`: maximum number of documents to fetch.

`score_threshold`: score below which a document is deemed irrelevant and not fetched.

`ìnsertion_mode`: `null` | `full` | `incremental`. [How document insertion in the vector store is handled.](https://python.langchain.com/docs/modules/data_connection/indexing#deletion-modes)