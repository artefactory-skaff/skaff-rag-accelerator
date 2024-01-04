import json

from langchain.callbacks.base import BaseCallbackHandler


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)

class LoggingCallbackHandler(BaseCallbackHandler):
    def __init__(self, logger, context: dict = None):
        self.logger = logger
        self.context = context or {}

    def _log_event(self, event_name, level, *args, **kwargs):
        if self.logger is None:
            return

        log_data = {
            "event": event_name,
            "context": self.context,
            "args": args,
            **kwargs,
        }
        log_message = json.dumps(log_data, cls=CustomJSONEncoder)
        if level == "info":
            self.logger.info(log_message)
        elif level == "error":
            self.logger.error(log_message)

    def on_llm_start(self, *args, **kwargs):
        self._log_event("llm_start", "info", *args, **kwargs)

    def on_llm_end(self, *args, **kwargs):
        self._log_event("llm_end", "info", *args, **kwargs)

    def on_retriever_error(self, *args, **kwargs):
        self._log_event("retriever_error", "error", *args, **kwargs)

    def on_retriever_end(self, *args, **kwargs):
        self._log_event("retriever_end", "info", *args, **kwargs)

    def on_llm_error(self, *args, **kwargs):
        self._log_event("llm_error", "error", *args, **kwargs)

    def on_chain_end(self, *args, **kwargs):
        self._log_event("chain_end", "info", *args, **kwargs)

    def on_chain_error(self, *args, **kwargs):
        self._log_event("chain_error", "error", *args, **kwargs)

    def on_agent_action(self, *args, **kwargs):
        self._log_event("agent_action", "info", *args, **kwargs)

    def on_agent_finish(self, *args, **kwargs):
        self._log_event("agent_finish", "info", *args, **kwargs)

    def on_tool_start(self, *args, **kwargs):
        self._log_event("tool_start", "info", *args, **kwargs)

    def on_tool_end(self, *args, **kwargs):
        self._log_event("tool_end", "info", *args, **kwargs)

    def on_tool_error(self, *args, **kwargs):
        self._log_event("tool_error", "error", *args, **kwargs)

    def on_text(self, *args, **kwargs):
        self._log_event("text", "info", *args, **kwargs)

    def on_retry(self, *args, **kwargs):
        self._log_event("retry", "info", *args, **kwargs)
