## Artefact Azure-hosted GPT4-turbo

```yaml
LLMConfig: &LLMConfig
  source: AzureChatOpenAI
  source_config:
    openai_api_type: azure
    openai_api_key: {{ OPENAI_API_KEY }}
    openai_api_base: https://genai-ds.openai.azure.com/
    openai_api_version: 2023-07-01-preview
    deployment_name: gpt4
  temperature: 0.1
```

## Vertex AI gemini-pro

!!! info "login to GCP"

    ```shell
    export PROJECT_ID=<gcp_project_id>
    gcloud config set project $PROJECT_ID
    gcloud auth login
    gcloud auth application-default login
    ```

```yaml
LLMConfig: &LLMConfig
  source: ChatVertexAI
  source_config:
    model_name: gemini-pro
  temperature: 0.1
```