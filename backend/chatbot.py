from pathlib import Path
from typing import List, Optional, Tuple, Union

import pandas as pd
from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
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
from langchain.memory.chat_message_histories import ChatMessageHistory
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    PromptTemplate,
)
from langchain.schema.document import Document
from langchain.schema.messages import HumanMessage, SystemMessage
from langchain.text_splitter import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)
from langchain.vectorstores import Chroma

from backend.llm import get_model_instance

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


def get_documents(data: pd.DataFrame) -> List[Document]:
    """Converts a dataframe into a list of Document objects."""
    docs = data["answer"].tolist()
    metadatas = data[["source", "question"]].to_dict("records")

    documents = []
    for text, metadata in zip(docs, metadatas):
        document = Document(page_content=text, metadata=metadata)
        documents.append(document)
    return documents


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
        raise Exception("Unsupported file type!")

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
    llm = get_model_instance()

    embeddings = get_embeddings_model("https://poc-openai-artefact.openai.azure.com/", "")

    documents = load_documents(".csv", str(Path(__file__).parent / "billionaires_csv.csv"))
    texts = get_chunks(documents, chunk_size=1500, chunk_overlap=200, text_splitter_type="recursive")
    docsearch = get_vector_store(texts, embeddings)
    msgs, memory = choose_memory_type(memory_type="buffer")
    answer_chain = get_answer_chain(llm, docsearch, memory)

    prompt = "Qui sont les 3 personnes les plus riches en france ?"
    response = get_response(answer_chain, prompt)
    print("Prompt :", prompt)
    print("Response: ", response)
