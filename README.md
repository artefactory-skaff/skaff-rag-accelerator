# skaff-rag-accelerator

This is a starter kit to prototype locally, deploy on any cloud, and industrialize a Retrival-Augmented Generation (RAG) service.

## Features

- A configurable RAG setup based around Langchain ([Check out the configuration cookbook here](https://artefactory.github.io/skaff-rag-accelerator/cookbook/))
- `RAG` and `RagConfig` python classes to help you set things up
- A REST API based on Langserve + FastAPI to provide easy access to the RAG as a web backend
- A demo Streamlit to serve as a basic working frontend
- A document loader for the RAG
- Optional plugins for secure user authentication and session management

## Quickstart

This quickstart will guide you through the steps to serve a RAG fully locally. You will run the API backend and frontend on your machine, which should allow you to run your first queries against the RAG.

For this exemple, we will be using the `tinyllama` LLM, the `BAAI/bge-base-en-v1.5` embedding model, and Chroma for the vector store. This allows this setup to be fully local, and independent of any external API (and thus, free). However, the relevance of answers will not be impressive.

Duration: ~15 minutes.

### Pre-requisites

- Ollama, to serve the LLM locally ([Download and install](https://ollama.com/))
- A few GB of disk space to host the models
- Tested with python 3.11 (may work with other versions)

Start the LLM server:
```python
ollama run tinyllama
```

In a fresh env:
```shell
pip install -r requirements.txt
```

You will need to set some env vars, either in a .env file at the project root, or just by exporting them like so:
```shell
export PYTHONPATH=.
export ADMIN_MODE=1
```

Start the backend server locally:
```shell
python -m uvicorn backend.main:app
```

Start the frontend demo
```shell
python -m streamlit run frontend/front.py
```

You should then be able to login and chat to the bot:

![](docs/login_and_chat.gif)

Right now the RAG does not have any document loaded, let's add a sample:
```shell
python data_sample/add_data_sample_to_rag.py
```

The RAG now has access to the information from your loaded documents:

![](docs/query_with_knowledge.gif)

## Documentation

To deep dive into under the hood, take a look at the documentation

[On github pages](https://artefactory.github.io/skaff-rag-accelerator/)

Or serve them locally:
```shell
mkdocs serve
```
Then go to http://localhost:8000/
