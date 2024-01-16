## Locally hosted embedding model from Hugging Face

This will download the selected model from the HF hub and make embeddings on the machine the backend is running on.
```shell
pip install sentence_transformers
```

```yaml
# backend/config.yaml
EmbeddingModelConfig: &EmbeddingModelConfig
  source: HuggingFaceEmbeddings
  source_config:
    model_name : 'BAAI/bge-base-en-v1.5'
```


## Artefact Azure-hosted embedding model

```yaml
# backend/config.yaml
EmbeddingModelConfig: &EmbeddingModelConfig
  source: OpenAIEmbeddings
  source_config:
    openai_api_type: azure
    openai_api_key: {{ EMBEDDING_API_KEY }}
    openai_api_base: https://poc-openai-artefact.openai.azure.com/
    deployment: embeddings
    chunk_size: 500
```

## AWS Bedrock

!!! info "You will first need to login to AWS"

    ```shell
    pip install boto3
    ```
    [Follow this guide to authenticate your machine](https://docs.aws.amazon.com/cli/latest/userguide/cli-authentication-user.html)

```yaml
# backend/config.yaml
EmbeddingModelConfig: &EmbeddingModelConfig
  source: BedrockEmbeddings
  source_config:
    model_id: 'amazon.titan-embed-text-v1'
```
