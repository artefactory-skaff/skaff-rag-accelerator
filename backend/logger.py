import logging
from logging import Logger

# Implement your custom logging logic here. Eg. send logs to a cloud's logging tool.
_logger_instance = None

def get_logger() -> Logger:
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = logging.getLogger(__name__)
        _logger_instance.setLevel(logging.INFO)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        _logger_instance.addHandler(console_handler)
    return _logger_instance
