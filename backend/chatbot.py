from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chat_models.base import HumanMessage, SystemMessage
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    PromptTemplate,
)
from langchain.vectorstores import VectorStore

from backend.config_renderer import get_config
from backend.rag_components.chat_message_history import get_conversation_buffer_memory
from backend.rag_components.embedding import get_embedding_model
from backend.rag_components.llm import get_llm_model
from backend.rag_components.vector_store import get_vector_store


def get_response(answer_chain: ConversationalRetrievalChain, query: str) -> str:
    """Processes the given query through the answer chain and returns the formatted response."""
    {
        "content": answer_chain.run(query),
    }
    return answer_chain.run(query)


def get_answer_chain(llm, docsearch: VectorStore, memory) -> ConversationalRetrievalChain:
    """Returns an instance of ConversationalRetrievalChain based on the provided parameters."""
    template = """Given the conversation history and the following question, can you rephrase the user's question in its original language so that it is self-sufficient. Make sure to avoid the use of unclear pronouns.

Chat history :
{chat_history}
Question : {question}

Rephrased question :
"""
    condense_question_prompt = PromptTemplate.from_template(template)
    condense_question_chain = LLMChain(
        llm=llm,
        prompt=condense_question_prompt,
    )

    messages = [
        SystemMessage(
            content=(
                """As a chatbot assistant, your mission is to respond to user inquiries in a precise and concise manner based on the documents provided as input. It is essential to respond in the same language in which the question was asked. Responses must be written in a professional style and must demonstrate great attention to detail."""
            )
        ),
        HumanMessage(content="Respond to the question taking into account the following context."),
        HumanMessagePromptTemplate.from_template("{context}"),
        HumanMessagePromptTemplate.from_template("Question: {question}"),
    ]
    system_prompt = ChatPromptTemplate(messages=messages)
    qa_chain = LLMChain(
        llm=llm,
        prompt=system_prompt,
    )

    doc_prompt = PromptTemplate(
        template="Content: {page_content}\nSource: {source}",
        input_variables=["page_content", "source"],
    )

    final_qa_chain = StuffDocumentsChain(
        llm_chain=qa_chain,
        document_variable_name="context",
        document_prompt=doc_prompt,
    )

    return ConversationalRetrievalChain(
        question_generator=condense_question_chain,
        retriever=docsearch.as_retriever(search_kwargs={"k": 10}),
        memory=memory,
        combine_docs_chain=final_qa_chain,
        verbose=True,
    )


if __name__ == "__main__":
    chat_id = "test"
    config = get_config()
    llm = get_llm_model(config)
    embeddings = get_embedding_model(config)
    vector_store = get_vector_store(embeddings, config)
    memory = get_conversation_buffer_memory(config, chat_id)
    answer_chain = get_answer_chain(llm, vector_store, memory)

    prompt = "Give me the top 5 bilionnaires in france based on their worth in order of decreasing net worth"
    response = get_response(answer_chain, prompt)
    print("Prompt: ", prompt)
    print("Response: ", response)
