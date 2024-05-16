"""This chain answers the provided question based on documents it retreives."""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import RunnablePassthrough
from pydantic import BaseModel

from backend.rag_components.chain_links.documented_runnable import DocumentedRunnable
from backend.rag_components.chain_links.retrieve_and_format_docs import fetch_docs_chain

prompt = """
As a chatbot assistant, your mission is to respond to user inquiries in a precise and concise manner based on the documents provided as input. It is essential to respond in the same language in which the question was asked. Responses must be written in a professional style and must demonstrate great attention to detail. Do not invent information. You must sift through various sources of information, disregarding any data that is not relevant to the query's context. Your response should integrate knowledge from the valid sources you have identified. Additionally, the question might include hypothetical or counterfactual statements. You need to recognize these and adjust your response to provide accurate, relevant information without being misled by the counterfactuals. Respond to the question only taking into account the following context. If no context is provided, do not answer. You may provide an answer if the user explicitely asked for a general answer. You may ask the user to rephrase their question, or their permission to answer without specific context from your own knowledge.
Context: {relevant_documents}

Question: {question}
"""  # noqa: E501


class Question(BaseModel):
    question: str


class Response(BaseModel):
    response: str


def rag_basic(llm, retriever: BaseRetriever) -> DocumentedRunnable:
    chain = (
        {
            "relevant_documents": fetch_docs_chain(retriever),
            "question": RunnablePassthrough(Question),
        }
        | ChatPromptTemplate.from_template(prompt)
        | llm
    )
    typed_chain = chain.with_types(input_type=str, output_type=Response)
    return DocumentedRunnable(
        typed_chain,
        chain_name="Answer questions from documents stored in a vector store",
        prompt=prompt,
        user_doc=__doc__,
    )
