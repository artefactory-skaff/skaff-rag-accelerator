from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables.history import RunnableWithMessageHistory
from backend.config import RagConfig

from backend.rag_components.chain_links.answer_question_from_docs_and_history import answer_question_from_docs_and_history_chain
from backend.rag_components.chain_links.documented_runnable import DocumentedRunnable
from backend.rag_components.chat_message_history import get_chat_message_history


def rag_with_history_chain(config: RagConfig, llm, retriever: BaseRetriever) -> DocumentedRunnable:
    chain = answer_question_from_docs_and_history_chain(llm, retriever)

    chain_with_mem = RunnableWithMessageHistory(
        chain,
        lambda session_id: get_chat_message_history(config, session_id),
        input_messages_key="question",
        history_messages_key="chat_history"
    )

    return chain_with_mem

    # A bug in DocumentedRunnable makes configurable Runnables such as RunnableWithMessageHistory not work properly.
    return DocumentedRunnable(
        chain_with_mem, 
        chain_name="RAG with persistant memory", 
        user_doc="This chain answers the provided question based on documents it retreives and the conversation history. It uses a persistant memory to store the conversation history.",
    )
