from uuid import uuid4

import streamlit as st

from dataclasses import dataclass
from streamlit_feedback import streamlit_feedback

@dataclass
class Message:
    user: str
    text: str
    id: str = None

    def __post_init__(self):
        self.id = str(uuid4()) if self.id is None else self.id

messages = []

def chat():
    prompt = st.chat_input("Say something")

    if prompt:
        messages.append(Message("user", prompt))
        response = send_prompt(prompt)
        messages.append(Message("assistant", response))

    with st.container(border=True):
        for message in messages:
            with st.chat_message(message.user):
                st.write(message.text)
        if len(messages) > 0 and len(messages) % 2 == 0:
            streamlit_feedback(key=str(len(messages)), feedback_type="thumbs", on_submit=lambda feedback: send_feedback(messages[-1].id, feedback))

def send_prompt(prompt: str):
    session = st.session_state.get("session")
    response = session.post("/chat/user_message", json={"prompt": prompt})
    return response.json()["message"]

def send_feedback(message_id: str, feedback: str):
    feedback = "thumbs_up" if feedback["score"] == "👍" else "thumbs_down"
    session = st.session_state.get("session")
    response = session.post(f"/feedback/{message_id}/{feedback}")
    return response.text