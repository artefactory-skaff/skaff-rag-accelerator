![](login_and_chat.gif)

The frontend is the end user facing part. It reaches out to the backend ONLY through the REST API. We provide a Streamlit frontend demo here for convenience, but ultimately it could live in a completely different repo, and be written in a completely different language.


!!! success ""
    As you work on this repo, it is advisable to keep the front and back decoupled. You can consider the `backend` and `frontend` folders to be two different, standalone repos.

    You may have code that looks like it would fit well in a `commons` directory and be used by both. In that case, prefer integrating it in the backend and making it available to the frontend via the API. You can also just duplicate the code if it's small enough.