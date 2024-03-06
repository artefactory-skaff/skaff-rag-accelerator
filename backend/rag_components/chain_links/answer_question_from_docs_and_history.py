"""This chain answers the provided question based on documents it retreives and the conversation history"""
from langchain_core.retrievers import BaseRetriever
from pydantic import BaseModel
from backend.rag_components.chain_links.rag_basic import rag_basic
from backend.rag_components.chain_links.condense_question import condense_question

from backend.rag_components.chain_links.documented_runnable import DocumentedRunnable
from backend.rag_components.chain_links.retrieve_and_format_docs import fetch_docs_chain


class QuestionWithHistory(BaseModel):
    question: str
    chat_history: str


class Response(BaseModel):
    response: str


def answer_question_from_docs_and_history_chain(llm, retriever: BaseRetriever) -> DocumentedRunnable:
    reformulate_question = condense_question(llm)
    answer_question = rag_basic(llm, retriever)

    chain =  reformulate_question | answer_question
    typed_chain = chain.with_types(input_type=QuestionWithHistory, output_type=Response)

    return DocumentedRunnable(typed_chain, chain_name="Answer question from docs and history", user_doc=__doc__)
