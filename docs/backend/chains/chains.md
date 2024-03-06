We provide two basic RAG chains to get you started, one does simple one-shot Q&A on your RAG, and the other is able handle conversation history.


[Basic chain documentation](basic_chain.md)

[Chain with memory documentation](chain_with_memory.md)

## Chains and chain links

This repo does not define large monolithic chains. To make it easier to pick and chose the required functionalities, we provide "chain links" at `backend/rag_components/chain_links`. All links are valid, self-sufficient chains. You can think of it as a toolbox of langchain components meant to be composed and stacked together to build actually useful chains. 

As all links are `Runnable` objects, they can be built from other chain links which are themselves made of chain links, etc...

This abstraction also makes it very easy to contribute now functionalities, as you can just develop a new chain link and add it here as a file.


Typically, a link has:

- Input and output pydantic models
- A prompt
- A chain definition


For example the `condense_question` chain link has `QuestionWithChatHistory` and `StandaloneQuestion` as input an output models. 
```python
class QuestionWithChatHistory(BaseModel):
    question: str
    chat_history: str


class StandaloneQuestion(BaseModel):
    standalone_question: str
```

It also has a prompt that uses the contents of `QuestionWithChatHistory` to formulate a question based on the chat history and the latest question.
```python
prompt = """\
Given the conversation history and the following question, can you rephrase the user's question in its original language so that it is self-sufficient. You are presented with a conversation that may contain some spelling mistakes and grammatical errors, but your goal is to understand the underlying question. Make sure to avoid the use of unclear pronouns.

If the question is already self-sufficient, return the original question. If it seem the user is authorizing the chatbot to answer without specific context, make sure to reflect that in the rephrased question.

Chat history: {chat_history}

Question: {question}
""" # noqa: E501
```

And finally a function that defines and returns the actual chain. Notice the `with_types` method that binds the pydantic models we defined ealier to the chains inputs and outputs. This is very useful to track your chain's execution and debug. The `DocumentedRunnable` object will be introduced and explained in the next section.
```python
def condense_history_chain(llm) -> DocumentedRunnable:
    condense_question_prompt = PromptTemplate.from_template(prompt)  # chat_history, question

    standalone_question = condense_question_prompt | llm | StrOutputParser()
    typed_chain = standalone_question.with_types(input_type=QuestionWithChatHistory, output_type=StandaloneQuestion)

    return DocumentedRunnable(typed_chain, chain_name="Condense question and history", prompt=prompt, user_doc=__doc__)
```

## Automated chain documentation

As the chains stack can get quite high and complex, it is useful to be able to explain and explore it. This is the goal of the `DocumentedRunnable`. This binds to a chain and generates markdown documentation from the input/outputs models, and other info you provide it: a prompt, or other documentation.

Documentation is recursively generated from all the `DocumentedRunnable` chains and sub-chains. Sub-chains documentation is nested in the top-level documentation.

!!! warning "Experimental"
    This feature is experimental and may have small quirks and bugs. Please do report them to alexis.vialaret@artefact.com so I can fix them. Contributions and feedback are also welcome.


In order to document your chain, just wrap it in a `DocumentedRunnable`:
```python
documented_chain = DocumentedRunnable(
    runnable=my_chain, 
    chain_name="My documented Chain", 
    user_doc="Additional chain explainations that will be displayed in the markdown", 
    prompt=prompt,
)
```

For example, let's generate documentation for the `condense_question` chain link:

```python
from backend.rag_components.chain_links.condense_question import condense_question
from langchain.llms.openai import OpenAIChat

llm = OpenAIChat()
chain = condense_question(llm)

print(chain.documentation)
```

<details markdown><summary>Generated documentation</summary>

## Condense question and history

This chain condenses the chat history and the question into one standalone question.


### Prompt
```
Given the conversation history and the following question, can you rephrase the user's question in its original language so that it is self-sufficient. You are presented with a conversation that may contain some spelling mistakes and grammatical errors, but your goal is to understand the underlying question. Make sure to avoid the use of unclear pronouns.

If the question is already self-sufficient, return the original question. If it seem the user is authorizing the chatbot to answer without specific context, make sure to reflect that in the rephrased question.

Chat history: {chat_history}

Question: {question}
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
