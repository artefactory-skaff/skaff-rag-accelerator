## RAG with persistant memory

This chain answers the provided question based on documents it retreives and the conversation history. It uses a persistant memory to store the conversation history.


### Input: Dict

### Output: Response

| Name         | Type   | Required   | Default   |
|--------------|--------|------------|-----------|
| **response** | str    | True       |           |



## Sub-chain

<details markdown><summary>Answer question from docs and history</summary>
## Answer question from docs and history

This chain answers the provided question based on documents it retreives and the conversation history



### Input: QuestionWithHistory

| Name             | Type   | Required   | Default   |
|------------------|--------|------------|-----------|
| **question**     | str    | True       |           |
| **chat_history** | str    | True       |           |



### Output: Response

| Name         | Type   | Required   | Default   |
|--------------|--------|------------|-----------|
| **response** | str    | True       |           |



## Sub-chain

<details markdown><summary>RunnableSequence</summary>
## RunnableSequence



### Input: QuestionWithChatHistory

| Name             | Type   | Required   | Default   |
|------------------|--------|------------|-----------|
| **question**     | str    | True       |           |
| **chat_history** | str    | True       |           |



### Output: Response

| Name         | Type   | Required   | Default   |
|--------------|--------|------------|-----------|
| **response** | str    | True       |           |



## These chains run in sequence

<details markdown><summary>Condense question and history</summary>
## Condense question and history

This chain condenses the chat history and the question into one standalone question.


### Prompt
```

<s>[INST] <<SYS>>
Given the conversation history and the following question, can you rephrase the user's question in its original language so that it is self-sufficient. You are presented with a conversation that may contain some spelling mistakes and grammatical errors, but your goal is to understand the underlying question. Make sure to avoid the use of unclear pronouns.

If the question is already self-sufficient, return the original question. If it seem the user is authorizing the chatbot to answer without specific context, make sure to reflect that in the rephrased question.
<</SYS>>

Chat history: {chat_history}

Question: {question}
[/INST]

```


### Input: QuestionWithChatHistory

| Name             | Type   | Required   | Default   |
|------------------|--------|------------|-----------|
| **question**     | str    | True       |           |
| **chat_history** | str    | True       |           |



### Output: StandaloneQuestion

| Name                    | Type   | Required   | Default   |
|-------------------------|--------|------------|-----------|
| **standalone_question** | str    | True       |           |



</details>

<details markdown><summary>Answer questions from documents stored in a vector store</summary>
## Answer questions from documents stored in a vector store

This chain answers the provided question based on documents it retreives.


### Prompt
```

As a chatbot assistant, your mission is to respond to user inquiries in a precise and concise manner based on the documents provided as input. It is essential to respond in the same language in which the question was asked. Responses must be written in a professional style and must demonstrate great attention to detail. Do not invent information. You must sift through various sources of information, disregarding any data that is not relevant to the query's context. Your response should integrate knowledge from the valid sources you have identified. Additionally, the question might include hypothetical or counterfactual statements. You need to recognize these and adjust your response to provide accurate, relevant information without being misled by the counterfactuals. Respond to the question only taking into account the following context. If no context is provided, do not answer. You may provide an answer if the user explicitely asked for a general answer. You may ask the user to rephrase their question, or their permission to answer without specific context from your own knowledge.
Context: {relevant_documents}

Question: {question}

```

### Input: str

### Output: Response

| Name         | Type   | Required   | Default   |
|--------------|--------|------------|-----------|
| **response** | str    | True       |           |



## Sub-chain

<details markdown><summary>Fetch documents</summary>
## Fetch documents

This chain fetches the relevant documents and combines them into a single string.


### Prompt
```
{page_content}
```


### Input: Question

| Name         | Type   | Required   | Default   |
|--------------|--------|------------|-----------|
| **question** | str    | True       |           |



### Output: Documents

| Name          | Type   | Required   | Default   |
|---------------|--------|------------|-----------|
| **documents** | str    | True       |           |



</details>


</details>


</details>


</details>

