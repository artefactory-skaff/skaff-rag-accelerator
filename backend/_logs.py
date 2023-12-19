import os
from typing import Any, Dict, List, Sequence

import streamlit as st
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema.document import Document


class StreamHandler(BaseCallbackHandler):
    """StreamHandler is a class that handles the streaming of text.

    It is a callback handler for a language model. \
    It displays the generated text in a Streamlit container \
    and handles the start of the language model and the generation of new tokens.
    """

    def __init__(
        self, container: st.delta_generator.DeltaGenerator, initial_text: str = ""
    ) -> None:
        """Initialize the StreamHandler."""
        self.container = container
        self.text = initial_text
        self.run_id_ignore_token = None

    def on_llm_start(
        self, serialized: dict, prompts: List[str], **kwargs: Dict[str, Any]  # noqa: ARG002
    ) -> None:
        """Handle the start of the language model."""
        if "Question reformulée :" in prompts[0]:
            self.run_id_ignore_token = kwargs.get("run_id")

    def on_llm_new_token(self, token: str, **kwargs: Dict[str, Any]) -> None:
        """Handle the generation of a new token by the language model."""
        if self.run_id_ignore_token == kwargs.get("run_id", False):
            return
        self.text += token
        self.container.markdown(self.text)


class PrintRetrievalHandler(BaseCallbackHandler):
    """PrintRetrievalHandler is a class that handles the retrieval of documents.

    It is a callback handler for a document retriever. \
    It displays the status and content of the retrieved documents in a Streamlit container.
    """

    def __init__(self, container: st.delta_generator.DeltaGenerator) -> None:
        """Initialize the PrintRetrievalHandler."""
        self.status = container.status("**Context Retrieval**")

    def on_retriever_start(
        self, serialized: Dict[str, Any], query: str, **kwargs: Dict[str, Any]  # noqa: ARG002
    ) -> None:
        """Handle the start of the document retrieval."""
        self.status.write(f"**Question:** {query}")
        self.status.update(label=f"**Context Retrieval:** {query}")

    def on_retriever_end(
        self, documents: Sequence[Document], **kwargs: Dict[str, Any]  # noqa: ARG002
    ) -> None:
        """Handle the end of the document retrieval."""
        for idx, doc in enumerate(documents):
            source = os.path.basename(doc.metadata["source"])  # noqa: PTH119
            self.status.write(f"**Document {idx} from {source}**")
            self.status.markdown(doc.page_content)
        self.status.update(state="complete")
