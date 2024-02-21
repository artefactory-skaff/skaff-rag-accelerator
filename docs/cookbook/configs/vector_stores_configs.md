## PostgreSQL

As we need a backend SQL database to store conversation history and other info, using Postgres as a vector store is very attractive for us. Implementeing all this functionalities using the same technology reduces deployment overhead and complexity.

[See the recipes for database configs here](databases_configs.md)

```shell
pip install psycopg2-binary pgvector
```

```yaml
# backend/config.yaml
VectorStoreConfig: &VectorStoreConfig
  source: PGVector
  source_config:
    connection_string: {{ DATABASE_URL }}

  retriever_search_type: similarity_score_threshold
  retriever_config:
    k: 20
    score_threshold: 0.5

  insertion_mode: null
```

`top_k`: maximum number of documents to fetch.

`score_threshold`: score below which a document is deemed irrelevant and not fetched.

`insertion_mode`: `null` | `full` | `incremental`. [How document indexing and insertion in the vector store is handled.](https://python.langchain.com/docs/modules/data_connection/indexing#deletion-modes)


## Local Chroma

```yaml
# backend/config.yaml
VectorStoreConfig: &VectorStoreConfig
  source: Chroma
  source_config:
    persist_directory: vector_database/
    collection_metadata:
      hnsw:space: cosine

  retriever_search_type: similarity_score_threshold
  retriever_config:
    k: 20
    score_threshold: 0.5

  insertion_mode: null
```

`persist_directory`: where, locally the Chroma database will be persisted.

`hnsw:space: cosine`: [distance function used. Default is `l2`.](https://docs.trychroma.com/usage-guide#changing-the-distance-function) Cosine is bounded [0; 1], making it easier to set a score threshold for retrival.

`top_k`: maximum number of documents to fetch.

`score_threshold`: score below which a document is deemed irrelevant and not fetched.

`insertion_mode`: `null` | `full` | `incremental`. [How document indexing and insertion in the vector store is handled.](https://python.langchain.com/docs/modules/data_connection/indexing#deletion-modes)
