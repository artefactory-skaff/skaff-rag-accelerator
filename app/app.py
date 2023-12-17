import os
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
from PIL import Image
from streamlit_feedback import streamlit_feedback

import lib.chatbot as utils

load_dotenv()
embedding_api_base = os.getenv("EMBEDDING_OPENAI_API_BASE")
embedding_api_key = os.getenv("EMBEDDING_API_KEY")
FASTAPI_URL = "http://localhost:8000"


if __name__ == "__main__":
    logo_chat = Image.open("app/assets/logo_chat.png")
    logo_tab = Image.open("app/assets/logo_tab.jpeg")
    logo_title = Image.open("app/assets/logo_title.jpeg")
    logo_user = Image.open("app/assets/logo_user.png")

    st.set_page_config(
        page_title="RAG ChatBot",
        page_icon=logo_tab,
    )

    col1, mid, col2 = st.columns([4, 4, 20])
    with col1:
        st.image(logo_title, width=100)
    with col2:
        st.title("RAG ChatBot demo")
    # st.caption(
    #     "Helloïz demo est un assistant IA offrant des conseils sur les offres \
    #     et services de la banque en ligne Hello Bank.\
    #     Il ne remplace pas un conseiller bancaire. Helloïz peut commettre des erreurs."
    # )

    msgs = StreamlitChatMessageHistory(key="special_app_key")
    memory = ConversationBufferMemory(
        memory_key="chat_history", chat_memory=msgs, return_messages=True
    )

    llm_40 = utils.get_llm(temperature=0.1, model_version="4", live_streaming=True)
    embeddings = utils.get_embeddings_model(embedding_api_base, embedding_api_key)

    documents = utils.load_documents(source="site")
    texts = utils.get_chunks(documents, chunk_size=1500, chunk_overlap=200)
    docsearch = utils.get_vector_store(texts, embeddings)
    answer_chain = utils.get_answer_chain(llm_40, docsearch, memory)

    if len(msgs.messages) == 0:
        msgs.add_ai_message(
            f"Bonjour {st.session_state['name']} !\
            Je suis Helloïz, comment puis-je vous aider ?"
        )

    for msg in msgs.messages:
        msg_content_formatted = utils.format_history_msg(msg.content)
        if msg.type == "ai":
            with st.chat_message(msg.type, avatar=logo_chat):
                st.markdown(msg_content_formatted)
        else:
            with st.chat_message(msg.type, avatar=logo_user):
                st.markdown(msg_content_formatted)

    if prompt := st.chat_input():
        st.chat_message("human", avatar=logo_user).write(prompt)
        with st.chat_message("ai", avatar=logo_chat):
            response = utils.get_response(answer_chain, prompt)
            st.markdown(response)

            feedback = streamlit_feedback(
                feedback_type="thumbs",
                optional_text_label="[Optional] Please provide an explanation",
            )

            if feedback:
                data_dict = {
                    "query": prompt,
                    "answer": response,
                    "user": st.session_state.get("name", False),
                    "horodate": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                    "feedback": feedback.get("feedback_type"),
                }
                print(data_dict)
