from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.schema import format_document
from langchain.vectorstores.base import VectorStore
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory

from backend.config import RagConfig
from backend.rag_components import prompts
from backend.rag_components.chat_message_history import get_chat_message_history
from backend.rag_components.llm import get_llm_model

DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(template="{page_content}")

def get_memory_chain(
    config: RagConfig,
    vector_store: VectorStore
):
    llm = get_llm_model(config)
    condense_question_prompt = PromptTemplate.from_template(prompts.condense_history)  # chat_history, question
    standalone_question = condense_question_prompt | llm | StrOutputParser()
    base_chain = get_base_chain(config, vector_store)
    chain =  standalone_question | base_chain

    chain_with_mem = RunnableWithMessageHistory(
        chain,
        lambda session_id: get_chat_message_history(config, session_id),
        input_messages_key="question",
        history_messages_key="chat_history"
    )

    return chain_with_mem


def get_base_chain(config: RagConfig, vector_store: VectorStore):
    llm = get_llm_model(config)
    retriever = vector_store.as_retriever(
        search_type=config.vector_store.retriever_search_type,
        search_kwargs=config.vector_store.retriever_config
    )

    question_answering_prompt = ChatPromptTemplate.from_template(prompts.respond_to_question)  # standalone_question, relevant_documents
    relevant_documents = retriever | _combine_documents

    chain = (
        {"relevant_documents": relevant_documents, "standalone_question": RunnablePassthrough()}
        | question_answering_prompt
        | llm
    )
    return chain

def _combine_documents(docs, document_prompt=DEFAULT_DOCUMENT_PROMPT, document_separator="\n\n"):
    doc_strings = [format_document(doc, document_prompt) for doc in docs]
    return document_separator.join(doc_strings)
