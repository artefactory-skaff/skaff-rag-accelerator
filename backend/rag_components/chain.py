import asyncio
from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.combine_documents.reduce import ReduceDocumentsChain
from langchain.chat_models.base import SystemMessage
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    PromptTemplate,
)
from langchain.vectorstores import VectorStore

from backend.config import RagConfig
from backend.rag_components.llm import get_llm_model
from backend.rag_components import prompts
from backend.rag_components.logging_callback_handler import LoggingCallbackHandler



async def get_response_stream(chain: ConversationalRetrievalChain, query: str, streaming_callback_handler) -> str:
    run = asyncio.create_task(chain.arun({"question": query}))

    async for token in streaming_callback_handler.aiter():
        yield token

    await run


def get_answer_chain(config: RagConfig, docsearch: VectorStore, memory, streaming_callback_handler, logging_callback_handler: LoggingCallbackHandler = None) -> ConversationalRetrievalChain:
    callbacks = [logging_callback_handler] if logging_callback_handler is not None else []
    
    condense_question_prompt = PromptTemplate.from_template(prompts.condense_history)
    condense_question_chain = LLMChain(llm=get_llm_model(config), prompt=condense_question_prompt, callbacks=callbacks)

    messages = [
        SystemMessage(content=prompts.rag_system_prompt),
        HumanMessagePromptTemplate.from_template(prompts.respond_to_question),
    ]
    question_answering_prompt = ChatPromptTemplate(messages=messages)
    streaming_llm = get_llm_model(config, callbacks=[streaming_callback_handler] + callbacks)
    question_answering_chain = LLMChain(llm=streaming_llm, prompt=question_answering_prompt, callbacks=callbacks)

    context_with_docs_prompt = PromptTemplate(template=prompts.document_context, input_variables=["page_content", "source"])
    
    stuffed_qa_chain = StuffDocumentsChain(
        llm_chain=question_answering_chain,
        document_variable_name="context",
        document_prompt=context_with_docs_prompt,
        callbacks=callbacks
    )

    chain = ConversationalRetrievalChain(
        question_generator=condense_question_chain,
        retriever=docsearch.as_retriever(search_type=config.vector_store.retreiver_search_type, search_kwargs=config.vector_store.retreiver_config),
        memory=memory,
        max_tokens_limit=config.max_tokens_limit,
        combine_docs_chain=stuffed_qa_chain,
        callbacks=callbacks
    )

    return chain
