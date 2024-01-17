import streamlit as st


def query(verb: str, url: str, **kwargs):
    session = st.session_state.get("session")
    response = getattr(session, verb)(url, **kwargs)

    if response.status_code == 401:
        st.session_state["session"] = None
        st.session_state["email"] = None
        st.session_state["login_status_level"] = "error"
        st.session_state["login_status_message"] = "Session expired. Please log in again."
        st.rerun()

    return response
