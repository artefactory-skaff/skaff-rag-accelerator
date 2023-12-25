import os

from langchain.memory import ConversationBufferWindowMemory
from langchain.memory.chat_message_histories import SQLChatMessageHistory

TABLE_NAME = "message_history"


def get_conversation_buffer_memory(config, chat_id):
    return ConversationBufferWindowMemory(
        memory_key="chat_history",
        chat_memory=get_chat_message_history(chat_id),
        return_messages=True,
        k=config["chat_message_history_config"]["window_size"],
    )

def get_chat_message_history(chat_id):
    return SQLChatMessageHistory(
        session_id=chat_id,
        connection_string=os.environ.get("DATABASE_URL"),
        table_name=TABLE_NAME,
    )
