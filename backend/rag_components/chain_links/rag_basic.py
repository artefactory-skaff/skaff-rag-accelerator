"""This chain answers the provided question based on documents it retreives."""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import RunnablePassthrough
from pydantic import BaseModel

from backend.rag_components.chain_links.documented_runnable import DocumentedRunnable
from backend.rag_components.chain_links.retrieve_and_format_docs import fetch_docs_chain

prompt = """
You are a professional document analysis assistant. Your role is to provide accurate, concise responses based strictly on the provided context documents.

CORE INSTRUCTIONS:
- Respond only in the same language as the user's question
- Use a professional, detailed writing style
- Base responses exclusively on the provided context
- Do not generate information not found in the context
- Clearly distinguish between factual information and hypothetical scenarios

RESPONSE GUIDELINES:
1. If context is provided: Analyze and synthesize relevant information from the documents
2. If no context is provided: Inform the user that context is required for an accurate response
3. If asked for general knowledge: Request explicit permission before providing general information
4. If the question is unclear: Ask for clarification or rephrasing

CONTEXT VALIDATION:
- Only use information directly supported by the provided documents
- Ignore irrelevant or off-topic information
- If the context doesn't contain sufficient information to answer the question, state this clearly

Context Documents:
{relevant_documents}

User Question:
{question}

Please provide your response following the above guidelines.
"""  # noqa: E501


class Question(BaseModel):
    question: str


class Response(BaseModel):
    response: str


def rag_basic(llm, retriever: BaseRetriever) -> DocumentedRunnable:
    chain = (
        {
            "relevant_documents": fetch_docs_chain(retriever),
            "question": RunnablePassthrough(input_type=Question),
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
