# skaff-rag-accelerator


This is a starter kit to deploy a modularizable RAG locally or on the cloud (or across multiple clouds)

## Features

- A configurable RAG setup based around Langchain
- `RAG` and `RagConfig` python classes to help you set things up
- A REST API based on FastAPI to provide easy access to the RAG as a web backend
- A demo Streamlit to serve as a basic working frontend (not production grade)
- A document loader for the RAG
- User authentication (unsecure for now, but usable for conversation history)
- User feedback collection
- Streamed responses

## Quickstart

In a fresh env:
```shell
pip install -r requirements.txt
```

You will need to set some env vars, either in a .env file at the project root, or just by exporting them like so:
```shell
export PYTHONPATH=.
export OPENAI_API_KEY="xxx"  # API key used to query the LLM
export EMBEDDING_API_KEY="xxx"  # API key used to query the embedding model
export DATABASE_URL="sqlite:///$(pwd)/database/db.sqlite3"  # For local developement only. You will need a real, cloud-based SQL database URL for prod.
```

Start the backend server locally
```shell
python -m uvicorn backend.main:app
```

Start the frontend demo
```shell
python -m streamlit run frontend/app.py
```

You should than be able to login and chat to the bot:

![](docs/login_and_chat.gif)

Right now the RAG does not have any document loaded, let's add a sample:
```shell
python data_sample/add_data_sample_to_rag.py
```

The RAG now has access to thn information from your loaded documents:

![](docs/query_with_knowledge.gif)

## Documentation

To deep dive into under the hood, take a look at the documentation

[On github pages](https://redesigned-umbrella-evz5np5.pages.github.io/)

Or serve them locally:
```shell
mkdocs serve
```
Then go to http://localhost:8000/
