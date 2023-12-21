import asyncio
from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chat_models.base import SystemMessage
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    PromptTemplate,
)
from langchain.vectorstores import VectorStore

from backend.rag_components.llm import get_llm_model
from backend.rag_components import prompts


async def get_response_stream(chain: ConversationalRetrievalChain, callback_handler, query: str) -> str:
    run = asyncio.create_task(chain.arun({"question": query}))

    async for token in callback_handler.aiter():
        yield token

    await run


def get_answer_chain(config, docsearch: VectorStore, memory) -> ConversationalRetrievalChain:
    condense_question_prompt = PromptTemplate.from_template(prompts.condense_history)
    condense_question_chain = LLMChain(llm=get_llm_model(config), prompt=condense_question_prompt)

    messages = [
        SystemMessage(content=prompts.rag_system_prompt),
        HumanMessagePromptTemplate.from_template(prompts.respond_to_question),
    ]
    question_answering_prompt = ChatPromptTemplate(messages=messages)
    streaming_llm, callback_handler = get_llm_model(config, streaming=True)
    question_answering_chain = LLMChain(llm=streaming_llm, prompt=question_answering_prompt)

    context_with_docs_prompt = PromptTemplate(template=prompts.document_context, input_variables=["page_content", "source"])
    
    final_qa_chain = StuffDocumentsChain(
        llm_chain=question_answering_chain,
        document_variable_name="context",
        document_prompt=context_with_docs_prompt,
    )

    chain = ConversationalRetrievalChain(
        question_generator=condense_question_chain,
        retriever=docsearch.as_retriever(search_kwargs={"k": config["vector_store_provider"]["documents_to_retreive"]}),
        memory=memory,
        combine_docs_chain=final_qa_chain,
    )

    return chain, callback_handler

