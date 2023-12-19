from typing import List, Optional, Tuple, Union

import streamlit as st
from langchain.chat_models import AzureChatOpenAI
from langchain.document_loaders import (
    CSVLoader,
    Docx2txtLoader,
    PyPDFLoader,
    UnstructuredExcelLoader,
    UnstructuredPowerPointLoader,
)
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import (
    ConversationBufferMemory,
    ConversationBufferWindowMemory,
    ConversationSummaryBufferMemory,
    ConversationSummaryMemory,
)
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
from langchain.text_splitter import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)
from langchain.vectorstores import Chroma


def get_llm(
    temperature: float, model_version: str, live_streaming: bool = False
) -> AzureChatOpenAI:
    """Returns an instance of AzureChatOpenAI based on the provided parameters."""
    if model_version == "4":
        llm = AzureChatOpenAI(
            deployment_name="gpt4v",
            temperature=temperature,
            openai_api_version="2023-07-01-preview",
            streaming=live_streaming,
            verbose=live_streaming,
        )
    elif model_version == "3.5":
        llm = AzureChatOpenAI(
            deployment_name="gpt-35-turbo",
            temperature=temperature,
            openai_api_version="2023-03-15-preview",
            streaming=live_streaming,
            verbose=live_streaming,
        )
    return llm


def get_embeddings_model(embedding_api_base: str, embedding_api_key: str) -> OpenAIEmbeddings:
    """Returns an instance of OpenAIEmbeddings based on the provided parameters."""
    return OpenAIEmbeddings(
        deployment="text-embedding-ada-002",
        openai_api_type="azure",
        openai_api_base=embedding_api_base,
        openai_api_key=embedding_api_key,
        chunk_size=16,
    )


def load_documents(file_extension: str, file_path: str):
    """Loads documents based on the file extension and path provided."""
    if file_extension == ".pdf":
        loader = PyPDFLoader(file_path)
    elif file_extension in [".csv"]:
        loader = CSVLoader(file_path, encoding="utf-8-sig", csv_args={"delimiter": "\t"})
    elif file_extension in [".xlsx"]:
        loader = UnstructuredExcelLoader(file_path, mode="elements")
    elif file_extension in [".pptx"]:
        loader = UnstructuredPowerPointLoader(file_path)
    elif file_extension in [".docx"]:
        loader = Docx2txtLoader(file_path)
    else:
        st.error("Unsupported file type!")

    return loader.load()


def get_chunks(
    _documents: List[str], chunk_size: int, chunk_overlap: int, text_splitter_type: int
) -> List[str]:
    """Splits the documents into chunks."""
    if text_splitter_type == "basic":
        text_splitter = CharacterTextSplitter(
            separator="\n\n",
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
    elif text_splitter_type == "recursive":
        text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", " "], chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
    return text_splitter.split_documents(_documents)


def get_vector_store(_texts: List[str], _embeddings: OpenAIEmbeddings) -> Chroma:
    """Returns an instance of Chroma based on the provided parameters."""
    return Chroma.from_documents(_texts, _embeddings)


def choose_memory_type(
    memory_type: str, llm: Optional[AzureChatOpenAI]
) -> Tuple[
    StreamlitChatMessageHistory,
    Union[
        ConversationBufferMemory,
        ConversationBufferWindowMemory,
        ConversationSummaryMemory,
        ConversationSummaryBufferMemory,
    ],
]:
    """Chooses the memory type for the conversation based on the provided memory_type string."""
    msgs = StreamlitChatMessageHistory(key="special_app_key")
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
            llm=llm, memory_key="chat_history", chat_memory=msgs, return_messages=True
        )
    elif memory_type == "summary_buffer":
        memory = ConversationSummaryBufferMemory(
            llm=llm,
            max_token_limit=100,
            memory_key="chat_history",
            chat_memory=msgs,
            return_messages=True,
        )
    return msgs, memory
