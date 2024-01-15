## Artefact Azure-hosted GPT4-turbo

```yaml
# backend/config.yaml
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

## Local llama2
!!! info "You will first need to install and run Ollama"

    [Download the Ollama application here](https://ollama.ai/download)

    Ollama will automatically utilize the GPU on Apple devices.

    ```shell
    ollama run llama2
    ```

```yaml
# backend/config.yaml
LLMConfig: &LLMConfig
  source: ChatOllama
  source_config:
    model: llama2
```

## Vertex AI gemini-pro

!!! info "You will first need to login to GCP"

    ```shell
    export PROJECT_ID=<gcp_project_id>
    gcloud config set project $PROJECT_ID
    gcloud auth login
    gcloud auth application-default login
    ```

!!! info ""
    <a href="https://console.cloud.google.com/vertex-ai" target="_blank">Activate the Vertex APIs in your project</a>

```yaml
# backend/config.yaml
LLMConfig: &LLMConfig
  source: ChatVertexAI
  source_config:
    model_name: gemini-pro
  temperature: 0.1
```
