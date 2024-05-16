"""This chain fetches the relevant documents and combines them into a single string."""

from langchain.schema import format_document
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel

from backend.rag_components.chain_links.documented_runnable import DocumentedRunnable

prompt = "{page_content}"


class Question(BaseModel):
    question: str


class Documents(BaseModel):
    documents: str


def fetch_docs_chain(retriever) -> DocumentedRunnable:
    relevant_documents = retriever | _combine_documents
    typed_chain = relevant_documents.with_types(
        input_type=Question, output_type=Documents
    )
    return DocumentedRunnable(
        typed_chain, chain_name="Fetch documents", prompt=prompt, user_doc=__doc__
    )


def _combine_documents(docs, document_separator="\n\n"):
    document_prompt = PromptTemplate.from_template(template=prompt)
    doc_strings = [format_document(doc, document_prompt) for doc in docs]
    return document_separator.join(doc_strings)
