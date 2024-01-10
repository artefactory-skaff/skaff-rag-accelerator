from operator import itemgetter

from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.schema import format_document
from langchain.vectorstores.base import VectorStore
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

from backend.config import RagConfig
from backend.rag_components import prompts
from backend.rag_components.llm import get_llm_model
from backend.rag_components.logging_callback_handler import LoggingCallbackHandler

DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(template="{page_content}")

def get_answer_chain(
        config: RagConfig,
        vector_store: VectorStore,
        memory: ConversationBufferWindowMemory,
        logging_callback_handler: LoggingCallbackHandler = None
    ):
    llm_callbacks = [logging_callback_handler] if logging_callback_handler is not None else []
    llm = get_llm_model(config, callbacks=llm_callbacks)

    retriever = vector_store.as_retriever(
        search_type=config.vector_store.retriever_search_type,
        search_kwargs=config.vector_store.retriever_config
    )

    condense_question_prompt = PromptTemplate.from_template(prompts.condense_history)
    question_answering_prompt = ChatPromptTemplate.from_template(prompts.respond_to_question)


    _inputs = RunnableParallel(
        standalone_question=RunnablePassthrough.assign(chat_history=lambda _: memory.buffer_as_str)
        | condense_question_prompt
        | llm
        | StrOutputParser(),
    )
    _context = {
        "context": itemgetter("standalone_question") | retriever | _combine_documents,
        "question": lambda x: x["standalone_question"],
    }
    conversational_qa_chain = _inputs | _context | question_answering_prompt | llm
    return conversational_qa_chain


def _combine_documents(docs, document_prompt=DEFAULT_DOCUMENT_PROMPT, document_separator="\n\n"):
    doc_strings = [format_document(doc, document_prompt) for doc in docs]
    return document_separator.join(doc_strings)
