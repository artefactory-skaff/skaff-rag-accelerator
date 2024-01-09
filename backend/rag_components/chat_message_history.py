import os

from langchain.memory import ConversationBufferWindowMemory
from langchain_community.chat_message_histories import SQLChatMessageHistory

from backend.config import RagConfig

TABLE_NAME = "message_history"


def get_conversation_buffer_memory(config: RagConfig, chat_id) -> ConversationBufferWindowMemory:
    return ConversationBufferWindowMemory(
        memory_key="chat_history",
        chat_memory=get_chat_message_history(config, chat_id),
        return_messages=True,
        k=config.chat_history_window_size,
    )

def get_chat_message_history(config: RagConfig, chat_id):
    return SQLChatMessageHistory(
        session_id=chat_id,
        connection_string=config.database.database_url,
        table_name=TABLE_NAME,
    )
