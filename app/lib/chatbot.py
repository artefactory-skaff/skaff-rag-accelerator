import json
from typing import List

import pandas as pd
import streamlit as st
from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chat_models import AzureChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    PromptTemplate,
)
from langchain.schema.document import Document
from langchain.schema.messages import HumanMessage, SystemMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma


@st.cache_resource
def get_llm(
    temperature: float, model_version: str, live_streaming: bool = False
) -> AzureChatOpenAI:
    """Returns an instance of AzureChatOpenAI based on the provided parameters."""
    if model_version == "4":
        llm = AzureChatOpenAI(
            deployment_name="gpt-4",
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


@st.cache_resource
def get_embeddings_model(embedding_api_base: str, embedding_api_key: str) -> OpenAIEmbeddings:
    """Returns an instance of OpenAIEmbeddings based on the provided parameters."""
    return OpenAIEmbeddings(
        deployment="text-embedding-ada-002",
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


@st.cache_data
def load_documents(source: str) -> List[Document]:
    """Loads documents from two CSV files and returns a combined list of these documents."""
    if source == "faq":
        data_faq = pd.read_csv(
            "../interface/assets/scraping_faq.csv", delimiter="\t", encoding="utf-8-sig"
        )
        documents = get_documents(data_faq)

    elif source == "site":
        data_site = pd.read_csv(
            "interface/assets/scraping_site.csv", delimiter="\t", encoding="utf-8-sig"
        )  # ../interface/assets/scraping_site.csv
        data_site["question"] = (
            data_site["source"].str.rsplit("/", n=2).str[-2].str.replace("-", " ")
        )
        data_site = data_site.rename(columns={"description": "answer"})
        documents = get_documents(data_site)

    elif source == "both":
        data_faq = pd.read_csv(
            "../interface/assets/scraping_faq.csv", delimiter="\t", encoding="utf-8-sig"
        )
        documents_faq = get_documents(data_faq)

        data_site = pd.read_csv(
            "../interface/assets/scraping_site.csv", delimiter="\t", encoding="utf-8-sig"
        )
        data_site["question"] = (
            data_site["source"].str.rsplit("/", n=2).str[-2].str.replace("-", " ")
        )
        data_site = data_site.rename(columns={"description": "answer"})
        documents_site = get_documents(data_site)
        documents = documents_faq + documents_site

    return documents


@st.cache_data
def get_chunks(_documents: List[str], chunk_size: int, chunk_overlap: int) -> List[str]:
    """Splits the documents into chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", " "], chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    return text_splitter.split_documents(_documents)


@st.cache_resource
def get_vector_store(_texts: List[str], _embeddings: OpenAIEmbeddings) -> Chroma:
    """Returns an instance of Chroma based on the provided parameters."""
    return Chroma.from_documents(_texts, _embeddings)


def get_answer_chain(
    llm: AzureChatOpenAI, docsearch: Chroma, memory: ConversationBufferMemory
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
                """En tant qu'assistant bancaire nommé Helloïz, spécialisé dans les
services de la banque en ligne Hello Bank, votre mission est de répondre de manière \
précise et concise aux interrogations des utilisateurs.
Il est essentiel de répondre dans la même langue que celle utilisée pour poser la question.
Les réponses doivent être rédigées dans un style professionnel et doivent faire preuve \
d'une grande attention aux détails.
Pour répondre à chaque question, veuillez structurer votre réponse sous la forme \
d'un objet JSON avec les clés suivantes :
- 'answer': Fournissez une réponse claire, précise et excacte à la question.
- 'source': Enumérez le contenu spécifique du document que vous avez utilisé pour formuler \
votre réponse.

Exemple :
{
"answer": "Si vous ne parvenez pas à effectuer un virement unitaire ou permanent, \
nous vous invitons à contacter la Hello Team.",
"source":  ["https://www.hellobank.fr/faq/mon-virement-a-ete-bloque-que-faire.html"]
}
"""
            )
        ),
        HumanMessage(content="Répondez à la question en prenant en compte le contexte suivant"),
        HumanMessagePromptTemplate.from_template("{context}"),
        HumanMessagePromptTemplate.from_template("Question: {question}"),
        HumanMessage(content="Tips: Make sure to answer in the specific JSON format requested."),
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


def format_chatbot_answer(response_msg: str) -> str:
    """Formats the chatbot's answer from a JSON string to a more readable string format."""
    response = response_msg.replace("\n\n", "\\n")
    json_response = json.loads(response)
    answer = json_response["answer"]
    source = json_response["source"]
    chatbot_answer = f"{answer}\n\n"
    for ref in source:
        add_ref = f"Pour en savoir plus, vous pouvez consulter la page suivante: {ref} \n\n"
        chatbot_answer += add_ref
    return chatbot_answer


def get_response(answer_chain: ConversationalRetrievalChain, query: str) -> str:
    """Processes the given query through the answer chain and returns the formatted response."""
    response = answer_chain.run(query)
    return format_chatbot_answer(response)


def format_history_msg(msg_content: str) -> str:
    """Formats the history message content."""
    if msg_content.startswith("{"):
        return format_chatbot_answer(msg_content)
    return msg_content
