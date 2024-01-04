## Artefact Azure-hosted embedding model

```yaml
EmbeddingModelConfig: &EmbeddingModelConfig
  source: OpenAIEmbeddings
  source_config:
    openai_api_type: azure
    openai_api_key: {{ EMBEDDING_API_KEY }}
    openai_api_base: https://poc-openai-artefact.openai.azure.com/
    deployment: embeddings
    chunk_size: 500
```
