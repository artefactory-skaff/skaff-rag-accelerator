from dataclasses import asdict, dataclass
from datetime import datetime
from uuid import uuid4

import streamlit as st
from streamlit_feedback import streamlit_feedback


@dataclass
class Message:
    sender: str
    content: str
    chat_id: str
    id: str = None
    timestamp: str = None

    def __post_init__(self):
        self.id = str(uuid4()) if self.id is None else self.id
        self.timestamp = datetime.now().isoformat() if self.timestamp is None else self.timestamp


def chat():
    prompt = st.chat_input("Say something")

    with st.container(border=True):
        for message in st.session_state.get("messages", []):
            with st.chat_message(message.sender):
                st.write(message.content)

        if prompt:
            if len(st.session_state.get("messages", [])) == 0:
                chat_id = new_chat()
            else:
                chat_id = st.session_state.get("chat_id")

            with st.chat_message("user"):
                st.write(prompt)

            user_message = Message("user", prompt, chat_id)
            st.session_state["messages"].append(user_message)

            response = send_prompt(user_message)
            with st.chat_message("assistant"):
                placeholder = st.empty()
                full_response = ""
                for item in response:
                    full_response += item
                    placeholder.write(full_response)
                placeholder.write(full_response)

            bot_message = Message("assistant", full_response, chat_id)
            st.session_state["messages"].append(bot_message)

        if (
            len(st.session_state.get("messages", [])) > 0
            and len(st.session_state.get("messages")) % 2 == 0
        ):
            streamlit_feedback(
                key=str(len(st.session_state.get("messages"))),
                feedback_type="thumbs",
                on_submit=lambda feedback: send_feedback(st.session_state.get("messages")[-1].id, feedback),
            )


def new_chat():
    session = st.session_state.get("session")
    response = session.post("/chat/new")
    st.session_state["chat_id"] = response.json()["chat_id"]
    st.session_state["messages"] = []
    return response.json()["chat_id"]


def send_prompt(message: Message):
    session = st.session_state.get("session")
    response = session.post(f"/chat/{message.chat_id}/user_message", stream=True, json=asdict(message))

    for line in response.iter_content(chunk_size=16, decode_unicode=True):
        yield line


def send_feedback(message_id: str, feedback: str):
    feedback = "thumbs_up" if feedback["score"] == "👍" else "thumbs_down"
    session = st.session_state.get("session")
    response = session.post(f"/feedback/{message_id}/{feedback}")
    return response.text
