import os
import tempfile
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from PIL import Image
from streamlit_feedback import streamlit_feedback

import interface.lib.chatbot as utils
from interface.lib.auth import login_form

load_dotenv()
embedding_api_base = os.getenv("EMBEDDING_OPENAI_API_BASE")
embedding_api_key = os.getenv("EMBEDDING_API_KEY")
FASTAPI_URL = "http://localhost:8000"


if __name__ == "__main__":
    logo_chat = Image.open("interface/assets/logo_chat.png")
    logo_tab = Image.open("interface/assets/logo_tab.jpeg")
    logo_title = Image.open("interface/assets/logo_title.jpeg")
    logo_user = Image.open("interface/assets/logo_user.png")

    st.set_page_config(
        page_title="RAG ChatBot",
        page_icon=logo_tab,
    )

    if not login_form():
        st.stop()

    st.image(logo_title)
    st.caption(
        "Démo d'un assistant IA, cloud agnostic, permettant de faire du RAG \
        sur différent type de document.\
        Le backend du ChatBot est APéïsé ce qui permet une meilleure scalabilité et robustesse."
    )

    uploaded_file = st.file_uploader("Upload a file", type=["pdf", "csv", "xlsx", "pptx", "docx"])

    if uploaded_file:
        temp_dir = tempfile.TemporaryDirectory()
        temp_filepath = os.path.join(temp_dir.name, uploaded_file.name)
        with open(temp_filepath, "wb") as f:
            f.write(uploaded_file.read())

        file_title, file_extension = os.path.splitext(uploaded_file.name)

        llm_40 = utils.get_llm(temperature=0.1, model_version="4", live_streaming=True)
        embeddings = utils.get_embeddings_model(embedding_api_base, embedding_api_key)

        documents = utils.load_documents(file_extension, temp_filepath)
        texts = utils.get_chunks(
            documents, chunk_size=1500, chunk_overlap=200, text_splitter_type="recursive"
        )
        docsearch = utils.get_vector_store(texts, embeddings)
        msgs, memory = utils.choose_memory_type(memory_type="buffer")
        answer_chain = utils.get_answer_chain(llm_40, docsearch, memory)

        if len(msgs.messages) == 0:
            msgs.add_ai_message(f"Bonjour ! Je suis le ChatBot Skaff, comment puis-je vous aider ?")

        for msg in msgs.messages:
            if msg.type == "ai":
                with st.chat_message(msg.type, avatar=logo_chat):
                    st.markdown(msg.content)
            else:
                with st.chat_message(msg.type, avatar=logo_user):
                    st.markdown(msg.content)

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
