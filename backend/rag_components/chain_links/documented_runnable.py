from typing import Any, Optional
from docdantic import get_field_info
from langchain_core.runnables.base import Runnable, RunnableBinding, RunnableBindingBase, RunnableSequence, RunnableParallel, RunnableConfig
from langchain_core.runnables.utils import Input, Output
from pydantic.main import ModelMetaclass
import tabulate
from jinja2 import Template


class DocumentedRunnable(RunnableBindingBase[Input, Output]):
    """A DocumentedRunnable is a wrapper around a Runnable that generates documentation.

    FIXME: Bound runnables that have configurable fields are not handled correctly, causing the playground to not be properly usable.
    TODO: Add Mermaid diagrams.

    This class is used to create a documented version of a Runnable, which is an executable
    unit of work in the langchain framework. The documentation includes information about
    the input and output types, as well as any additional user-provided prompts or documentation.

    Attributes:
        documentation (str): The generated markdown documentation for the Runnable.

    Args:
        runnable (Runnable): The Runnable to be documented.
        chain_name (Optional[str]): The name of the chain that the Runnable belongs to.
        prompt (Optional[str]): The prompt that the Runnable uses, if applicable.
        user_doc (Optional[str]): Any additional documentation you want displayed in the documentation.
    """

    documentation: str

    def __init__(
        self, 
        runnable: Runnable[Input, Output], 
        chain_name: Optional[str]=None, 
        prompt: Optional[str]=None, 
        user_doc: Optional[str]=None,
        **kwargs: Any,
    ) -> None:

        io_doc = render_io_doc(runnable)
        custom_input_type = runnable.input_schema
        custom_output_type = runnable.output_schema

        if hasattr(runnable, 'bound'):
            runnable = runnable.bound
    
        chain_name = chain_name or type(runnable).__name__

        if isinstance(runnable, RunnableSequence):
            sub_docs = [runnable.documentation if isinstance(runnable, DocumentedRunnable) else DocumentedRunnable(runnable).documentation for runnable in runnable.steps]
            sub_docs = [doc for doc in sub_docs if doc]
            documentation = render_documentation(chain_name, prompt, io_doc, sub_docs, user_doc)
        
        elif isinstance(runnable, RunnableParallel):
            sub_docs = [runnable.documentation if isinstance(runnable, DocumentedRunnable) else DocumentedRunnable(runnable).documentation for runnable in runnable.steps.values()]
            sub_docs = [doc for doc in sub_docs if doc]
            documentation = render_documentation(chain_name, prompt, io_doc, sub_docs, user_doc)
        
        elif isinstance(runnable, DocumentedRunnable):
            sub_docs = [runnable.documentation if isinstance(runnable, DocumentedRunnable) else DocumentedRunnable(runnable).documentation for _, runnable in runnable.bound if runnable]
            sub_docs = [doc for doc in sub_docs if doc]
            documentation = render_documentation(chain_name, prompt, io_doc, sub_docs, user_doc=user_doc)
        
        elif isinstance(runnable, RunnableBinding):
            lel = runnable.bound.steps
            sub_docs = [runnable.documentation if isinstance(runnable, DocumentedRunnable) else DocumentedRunnable(runnable).documentation for runnable in runnable.bound.steps if runnable]
            sub_docs = [doc for doc in sub_docs if doc]
            documentation = render_documentation(chain_name, prompt, io_doc, sub_docs, user_doc)
        
        else:
            documentation = ""

        super().__init__(
            bound=runnable, 
            documentation=documentation,
            custom_input_type=custom_input_type,
            custom_output_type=custom_output_type,
            **kwargs,
        )


def render_io_doc(runnable: Runnable) -> str:
    if isinstance(runnable.InputType, ModelMetaclass):
        input_doc = render_model_doc(runnable.InputType, "Input")
    else:
        input_doc = f"### Input: {runnable.InputType.__name__}"
    
    if isinstance(runnable.OutputType, ModelMetaclass):
        output_doc = render_model_doc(runnable.OutputType, "Output")
    else:
        output_doc = f"### Output: {runnable.OutputType.__name__}"

    io_doc = f"""{input_doc}\n\n{output_doc}\n\n"""
    return io_doc


def render_model_doc(model, input_or_output: str) -> str:
    field_info = get_field_info(model)

    tables = {
        cls: tabulate.tabulate(
            [
                (field.name, field.type, field.required, field.default,)
                for field in fields
            ],
            headers=["Name", "Type", "Required", "Default"],
            tablefmt="github"
        )
        for cls, fields in field_info.items()
    }

    return '\n'.join(
        f"\n### {input_or_output}: {cls}\n\n{table}\n\n"
        for cls, table in tables.items()
    )


def render_documentation(chain_name, prompt, io_doc, sub_docs=None, user_doc=None):
    template_str = """## {{ chain_name }}
{% if user_doc %}
{{ user_doc }}
{% endif %}
{% if prompt %}
### Prompt
```
{{ prompt }}
```
{% endif %}
{{ io_doc }}
{% if sub_docs %}
## Sub-chains
{% for doc in sub_docs %}
<details markdown><summary>{{ doc.splitlines()[0].replace('#', '').strip() }}</summary>
{{ doc }}
</details>
{% endfor %}
{% endif %}"""
    template = Template(template_str)
    return template.render(
        chain_name=chain_name,
        prompt=prompt,
        io_doc=io_doc,
        sub_docs=sub_docs,
        user_doc=user_doc
    )
