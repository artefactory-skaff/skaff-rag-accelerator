condense_history = """
Given the conversation history and the following question, can you rephrase the user's question in its original language so that it is self-sufficient. Make sure to avoid the use of unclear pronouns.

Chat history :
{chat_history}
Question : {question}

Rephrased question :
"""

rag_system_prompt = """
As a chatbot assistant, your mission is to respond to user inquiries in a precise and concise manner based on the documents provided as input.
It is essential to respond in the same language in which the question was asked. Responses must be written in a professional style and must demonstrate great attention to detail.
"""

respond_to_question = """
As a chatbot assistant, your mission is to respond to user inquiries in a precise and concise manner based on the documents provided as input.
It is essential to respond in the same language in which the question was asked. Responses must be written in a professional style and must demonstrate great attention to detail.


Respond to the question taking into account the following context. 

{context} 

Question: {question}
"""

document_context = """
Content: {page_content}

Source: {source}
"""