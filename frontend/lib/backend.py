import streamlit as st

def query(verb: str, url: str, **kwargs):
    session = st.session_state.get("session")
    response = getattr(session, verb)(url, **kwargs)

    if response.status_code == 401:
        st.session_state["session"] = None
        st.session_state["email"] = None
        st.rerun()
    
    return response