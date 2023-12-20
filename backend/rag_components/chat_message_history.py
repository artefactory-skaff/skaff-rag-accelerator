from langchain.memory import chat_message_histories
from langchain.memory import ConversationBufferWindowMemory

def get_chat_message_history(config):
    spec = getattr(chat_message_histories, config["chat_message_history_config"]["source"])
    kwargs = {
        key: value for key, value in config["chat_message_history_config"].items() if key in spec.__fields__.keys()
    }
    return spec(**kwargs)

def get_conversation_buffer_memory(config):
    return ConversationBufferWindowMemory(
        memory_key="chat_history", 
        chat_memory=get_chat_message_history(config), 
        return_messages=True,
        k=config["chat_message_history_config"]["window_size"]
    )