import json
import os
from datetime import datetime
from typing import Any
from uuid import uuid4

from langchain.memory import ConversationBufferWindowMemory
from langchain.memory.chat_message_histories import SQLChatMessageHistory
from langchain.memory.chat_message_histories.sql import DefaultMessageConverter
from langchain.schema import BaseMessage
from langchain.schema.messages import BaseMessage, _message_to_dict
from sqlalchemy import Column, DateTime, Text
from sqlalchemy.orm import declarative_base

TABLE_NAME = "message"


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
        connection_string=os.environ.get("DATABASE_CONNECTION_STRING"),
        table_name=TABLE_NAME,
        session_id_field_name="chat_id",
        custom_message_converter=CustomMessageConverter(table_name=TABLE_NAME),
    )


Base = declarative_base()


class CustomMessage(Base):
    __tablename__ = TABLE_NAME

    id = Column(
        Text, primary_key=True, default=lambda: str(uuid4())
    )  # default=lambda: str(uuid4())
    timestamp = Column(DateTime)
    chat_id = Column(Text)
    sender = Column(Text)
    content = Column(Text)
    message = Column(Text)


class CustomMessageConverter(DefaultMessageConverter):
    def to_sql_model(self, message: BaseMessage, session_id: str) -> Any:
        print(message.content)
        sub_message = json.loads(message.content)
        return CustomMessage(
            id=sub_message["id"],
            timestamp=datetime.strptime(sub_message["timestamp"], "%Y-%m-%d %H:%M:%S.%f"),
            chat_id=session_id,
            sender=message.type,
            content=sub_message["content"],
            message=json.dumps(_message_to_dict(message)),
        )

    def get_sql_model_class(self) -> Any:
        return CustomMessage
