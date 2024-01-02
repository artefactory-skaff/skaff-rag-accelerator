import os
from typing import Optional
from urllib.parse import urljoin

import extra_streamlit_components as stx
import requests
import streamlit as st
from requests.sessions import Session

FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000/")


def auth() -> Optional[str]:
    tab = stx.tab_bar(
        data=[
            stx.TabBarItemData(id="Login", title="Login", description=""),
            stx.TabBarItemData(id="Signup", title="Signup", description=""),
        ],
        default="Login",
    )
    if tab == "Login":
        return login_form()
    elif tab == "Signup":
        return signup_form()
    else:
        st.error("Invalid auth mode")
        return None


def login_form() -> tuple[bool, Optional[str]]:
    with st.form("Login"):
        username = st.text_input("Username", key="username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Log in")

        if submit:
            session = None
            token = get_token(username, password)
            if token:
                session = create_session()
                session = authenticate_session(session, token)
            else:
                st.error("Failed authentication")
            st.session_state["session"] = session
            st.session_state["email"] = username
            return session


def signup_form() -> tuple[bool, Optional[str]]:
    with st.form("Signup"):
        username = st.text_input("Username", key="username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Sign up")

        if submit:
            auth_session = None
            success = sign_up(username, password)
            if success:
                token = get_token(username, password)
                session = create_session()
                auth_session = authenticate_session(session, token)
            else:
                st.error("Failed signing up")
            st.session_state["session"] = auth_session
            st.session_state["email"] = username
            return auth_session


def get_token(username: str, password: str) -> Optional[str]:
    session = create_session()
    response = session.post("/user/login", data={"username": username, "password": password})
    if response.status_code == 200 and "access_token" in response.json():
        return response.json()["access_token"]
    else:
        return None


def sign_up(username: str, password: str) -> bool:
    session = create_session()
    response = session.post("/user/signup", json={"email": username, "password": password})
    if response.status_code == 200 and "email" in response.json():
        return True
    else:
        return False


def create_session() -> requests.Session:
    session = BaseUrlSession(FASTAPI_URL)
    return session


def authenticate_session(session, bearer_token: str) -> requests.Session:
    session.headers.update({"Authorization": f"Bearer {bearer_token}"})
    return session


class BaseUrlSession(Session):
    def __init__(self, base_url):
        super().__init__()
        self.base_url = base_url

    def request(self, method, url, *args, **kwargs):
        if not self.base_url.endswith("/"):
            self.base_url += "/"
        if url.startswith("/"):
            url = url[1:]
        url = urljoin(self.base_url, url)
        return super().request(method, url, *args, **kwargs)
