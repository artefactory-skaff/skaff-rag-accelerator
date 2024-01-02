import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from PIL import Image

from frontend.lib.auth import auth
from frontend.lib.chat import chat
from frontend.lib.sidebar import sidebar

load_dotenv()
FASTAPI_URL = os.getenv("FASTAPI_URL", "localhost:8000")

assets = Path(__file__).parent / "assets"


if __name__ == "__main__":
    st.set_page_config(
        page_title="RAG ChatBot",
        page_icon=Image.open(assets / "logo_tab.jpeg"),
    )

    if st.session_state.get("session", None) is None:
        session = auth()
        st.stop()

    logo_chat = Image.open(assets / "logo_chat.png")
    logo_user = Image.open(assets / "logo_user.png")

    st.image(Image.open(assets / "logo_title.jpeg"))
    st.caption(
        "Démo d'un assistant IA, cloud agnostic, permettant de faire du RAG \
        sur différent types de document.\
        Le backend du ChatBot est APéïsé ce qui permet une meilleure scalabilité et robustesse."
    )

    sidebar()
    chat()
