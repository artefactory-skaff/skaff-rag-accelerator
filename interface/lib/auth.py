from typing import Optional

import streamlit as st
from fastapi.testclient import TestClient

from lib.main import app

client = TestClient(app)


def log_in(username: str, password: str) -> Optional[str]:
    response = client.post("/user/login", data={"username": username, "password": password})
    if response.status_code == 200 and "access_token" in response.json():
        return response.json()["access_token"]
    else:
        return None


def sign_up(username: str, password: str) -> str:
    response = client.post("/user/signup", json={"username": username, "password": password})
    if response.status_code == 200 and "email" in response.json():
        return f"User {username} registered successfully."
    else:
        return "Registration failed."


def reset_pwd(username: str) -> str:
    # Assuming there's an endpoint to request a password reset
    response = client.post("/user/reset-password", json={"username": username})
    if response.status_code == 200:
        return "Password reset link sent."
    else:
        return "Failed to send password reset link."


def login_form():
    """Form with widgets to collect user information."""
    action = st.selectbox("Choose Action", ["Log in", "Sign up", "Reset Password"])

    with st.form("Credentials"):
        username = st.text_input("Username")
        # Password should not be asked when the user wants to reset the password
        password = st.text_input("Password", type="password") if action != "Reset Password" else ""

        submitted = st.form_submit_button("Submit")

        if submitted:
            if action == "Log in":
                token = log_in(username, password)
                if token:
                    st.success("Logged in successfully.")
                    # You can use the token here to make authenticated requests
                else:
                    st.error("Login failed.")
            elif action == "Sign up":
                result = sign_up(username, password)
                st.info(result)
            elif action == "Reset Password":
                result = reset_pwd(username, password)
                st.info(result)
