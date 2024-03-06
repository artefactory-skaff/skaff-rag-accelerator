from langchain_core.vectorstores import VectorStore
from langchain import retrievers as base_retrievers
from langchain_community import retrievers as community_retrievers


def get_retriever(vector_store: VectorStore):
    return vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"score_threshold": 0.5, "k": 5},
    )
