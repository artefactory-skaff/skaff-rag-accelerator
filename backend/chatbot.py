from pathlib import Path
from typing import List, Optional, Tuple, Union

from config_renderer import get_config
from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chat_models import AzureChatOpenAI
from langchain.document_loaders import DirectoryLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import (
    ConversationBufferMemory,
    ConversationBufferWindowMemory,
    ConversationSummaryBufferMemory,
    ConversationSummaryMemory,
)
from langchain.memory.chat_message_histories import ChatMessageHistory
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    PromptTemplate,
)
from langchain.schema.messages import HumanMessage, SystemMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma

from backend.embedding import get_embedding_model_instance
from backend.llm import get_llm_model_instance
from backend.vector_store import get_vector_store


def get_response(answer_chain: ConversationalRetrievalChain, query: str) -> str:
    """Processes the given query through the answer chain and returns the formatted response."""
    return answer_chain.run(query)


def get_answer_chain(
    llm, docsearch: Chroma, memory: ConversationBufferMemory
) -> ConversationalRetrievalChain:
    """Returns an instance of ConversationalRetrievalChain based on the provided parameters."""
    template = """Étant donné l'historique de conversation et la question suivante, \
pouvez-vous reformuler dans sa langue d'origine la question de l'utilisateur \
pour qu'elle soit auto porteuse. Assurez-vous d'éviter l'utilisation de pronoms peu clairs.

Historique de chat :
{chat_history}
Question complémentaire : {question}

Question reformulée :
"""
    condense_question_prompt = PromptTemplate.from_template(template)
    condense_question_chain = LLMChain(
        llm=llm,
        prompt=condense_question_prompt,
    )

    messages = [
        SystemMessage(
            content=(
                """En tant qu'assistant chatbot, votre mission est de répondre de manière \
précise et concise aux interrogations des utilisateurs à partir des documents donnés en input.
Il est essentiel de répondre dans la même langue que celle utilisée pour poser la question.
Les réponses doivent être rédigées dans un style professionnel et doivent faire preuve \
d'une grande attention aux détails.
"""
            )
        ),
        HumanMessage(content="Répondez à la question en prenant en compte le contexte suivant"),
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
        retriever=docsearch.as_retriever(),
        memory=memory,
        combine_docs_chain=final_qa_chain,
        verbose=False,
    )


def get_embeddings_model(embedding_api_base: str, embedding_api_key: str) -> OpenAIEmbeddings:
    """Returns an instance of OpenAIEmbeddings based on the provided parameters."""
    return OpenAIEmbeddings(
        deployment="embeddings",
        openai_api_type="azure",
        openai_api_base=embedding_api_base,
        openai_api_key=embedding_api_key,
        chunk_size=16,
    )


def text_chunker(
    directory_path: Path,
    chunk_size: int,
    chunk_overlap: int,
    separators: Optional[List[str]] = ["\n\n", "\n", "\t"],
):
    loader = DirectoryLoader(directory_path, glob="**/*.txt")
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        separators=separators, chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    return text_splitter.split_documents(docs)


def choose_memory_type(
    memory_type: str, _llm: Optional[AzureChatOpenAI] = None
) -> Tuple[
    ChatMessageHistory,
    Union[
        ConversationBufferMemory,
        ConversationBufferWindowMemory,
        ConversationSummaryMemory,
        ConversationSummaryBufferMemory,
    ],
]:
    """Chooses the memory type for the conversation based on the provided memory_type string."""
    msgs = ChatMessageHistory(key="special_app_key")
    if memory_type == "buffer":
        memory = ConversationBufferMemory(
            memory_key="chat_history", chat_memory=msgs, return_messages=True
        )
    elif memory_type == "buffer_window":
        memory = ConversationBufferWindowMemory(
            k=2, memory_key="chat_history", chat_memory=msgs, return_messages=True
        )
    elif memory_type == "summary":
        memory = ConversationSummaryMemory(
            llm=_llm, memory_key="chat_history", chat_memory=msgs, return_messages=True
        )
    elif memory_type == "summary_buffer":
        memory = ConversationSummaryBufferMemory(
            llm=_llm,
            max_token_limit=100,
            memory_key="chat_history",
            chat_memory=msgs,
            return_messages=True,
        )
    return msgs, memory


if __name__ == "__main__":
    config = get_config()
    llm = get_llm_model_instance(config)
    embeddings = get_embedding_model_instance(config)
    vector_store = get_vector_store(embeddings)
    texts = text_chunker(
        directory_path=Path(__file__).parent.parent / "data/",
        chunk_size=2000,
        chunk_overlap=200,
    )
    vector_store.add_documents(texts)
    msgs, memory = choose_memory_type(memory_type="buffer")
    answer_chain = get_answer_chain(llm, vector_store, memory)

    # prompt = "Qui sont les 3 personnes les plus riches en france ?"
    prompt = "Combien y a t'il de milliardaires en France ?"
    response = get_response(answer_chain, prompt)
    print("Prompt :", prompt)
    print("Response: ", response)
