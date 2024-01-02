from multiprocessing import Queue
from typing import AnyStr
from langchain_core.callbacks.base import BaseCallbackHandler

class StreamingCallbackHandler(BaseCallbackHandler):
    queue = Queue()

    def on_llm_new_token(self, token: str, **kwargs: AnyStr) -> None:
        """Run on new LLM token. Only available when streaming is enabled."""
        if token is not None and token != "":
            self.queue.put_nowait(token)
