from langchain_core.vectorstores import VectorStore


def get_retriever(vector_store: VectorStore):
    return vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"score_threshold": 0.5, "k": 5},
    )
