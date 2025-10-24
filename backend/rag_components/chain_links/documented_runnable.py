from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any, List, Optional

import tabulate
from docdantic import get_field_info
from jinja2 import Template
from langchain_core.runnables.base import (
    Runnable,
    RunnableBinding,
    RunnableBindingBase,
    RunnableParallel,
    RunnableSequence,
)
from langchain_core.runnables.utils import Input, Output
from pydantic.main import ModelMetaclass


@dataclass
class RunnableSequenceDocumentation:
    docs: List[RunnableDocumentation]


@dataclass
class RunnableParallelDocumentation:
    docs: List[RunnableDocumentation]


@dataclass
class RunnableBindingDocumentation:
    docs: List[RunnableDocumentation]


@dataclass
class RunnableDocumentation:
    chain_name: str
    prompt: Optional[str] = None
    input_type: Optional[Any] = None
    output_type: Optional[Any] = None
    user_doc: Optional[str] = None
    sub_docs: Optional[Any] = None

    def to_json(self):
        class EnhancedJSONEncoder(json.JSONEncoder):
            def default(self, o):
                return o.__name__

        return json.dumps(asdict(self), cls=EnhancedJSONEncoder)

    def to_markdown(self) -> str:
        rendered_sub_docs = ""
        if self.sub_docs:
            if isinstance(self.sub_docs, RunnableSequenceDocumentation):
                template = sequence_chains_template
            elif isinstance(self.sub_docs, RunnableParallelDocumentation):
                template = parallel_chains_template
            elif isinstance(self.sub_docs, RunnableBindingDocumentation):
                template = binding_chains_template

            sub_docs_markdown = [doc.to_markdown() for doc in self.sub_docs.docs]
            rendered_sub_docs = Template(template).render(docs=sub_docs_markdown)

        input_doc, output_doc = render_io_doc(self.input_type, self.output_type)
        return Template(markdown_doc_template).render(
            chain_name=self.chain_name,
            prompt=self.prompt,
            io_doc=input_doc + "\n" + output_doc,
            sub_docs=rendered_sub_docs,
            user_doc=self.user_doc,
        )


class DocumentedRunnable(RunnableBindingBase[Input, Output]):
    """A DocumentedRunnable is a wrapper around a Runnable that generates documentation.

    FIXME: Bound runnables that have configurable fields are not handled correctly,
        causing the playground to not be properly usable.
    TODO: Add Mermaid diagrams.

    This class is used to create a documented version of a Runnable, which is an
    executable unit of work in the langchain framework. The documentation includes
    information about the input and output types, as well as any additional
    user-provided prompts or documentation.

    Attributes:
        documentation (str): The generated markdown documentation for the Runnable.

    Args:
        runnable (Runnable): The Runnable to be documented.
        chain_name (Optional[str]): The name of the chain that the Runnable belongs to.
        prompt (Optional[str]): The prompt that the Runnable uses, if applicable.
        user_doc (Optional[str]): Any additional documentation you want displayed in the
            documentation.
    """

    documentation: RunnableDocumentation | None

    def __init__(
        self,
        runnable: Runnable[Input, Output],
        chain_name: Optional[str] = None,
        prompt: Optional[str] = None,
        user_doc: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        custom_input_type = runnable.InputType
        custom_output_type = runnable.OutputType
        final_chain_name = chain_name or type(runnable).__name__

        if isinstance(runnable, RunnableSequence):
            sub_docs = [
                (
                    runnable.documentation
                    if isinstance(runnable, DocumentedRunnable)
                    else DocumentedRunnable(runnable).documentation
                )
                for runnable in runnable.steps
            ]
            sub_docs = [doc for doc in sub_docs if doc]
            if len(sub_docs) >= 2:
                documentation = RunnableDocumentation(
                    chain_name=final_chain_name,
                    prompt=prompt,
                    input_type=custom_input_type,
                    output_type=custom_output_type,
                    user_doc=user_doc,
                    sub_docs=RunnableSequenceDocumentation(docs=sub_docs),
                )
            else:
                documentation = sub_docs[0] if len(sub_docs) else None

        elif isinstance(runnable, RunnableParallel):
            sub_docs = [
                (
                    runnable.documentation
                    if isinstance(runnable, DocumentedRunnable)
                    else DocumentedRunnable(runnable).documentation
                )
                for runnable in runnable.steps__.values()
            ]
            sub_docs = [doc for doc in sub_docs if doc]
            if len(sub_docs) >= 2:
                documentation = RunnableDocumentation(
                    chain_name=final_chain_name,
                    prompt=prompt,
                    input_type=custom_input_type,
                    output_type=custom_output_type,
                    user_doc=user_doc,
                    sub_docs=RunnableParallelDocumentation(docs=sub_docs),
                )
            else:
                documentation = sub_docs[0] if len(sub_docs) else None

        elif hasattr(runnable, "bound"):
            bound_runnable = runnable.bound
            while isinstance(bound_runnable, RunnableBinding):
                bound_runnable = bound_runnable.bound

            sub_docs = [
                bound_runnable.documentation
                if isinstance(bound_runnable, DocumentedRunnable)
                else DocumentedRunnable(bound_runnable).documentation
            ]
            sub_docs = [doc for doc in sub_docs if doc]

            if final_chain_name == "RunnableBinding":
                documentation = sub_docs[0] if len(sub_docs) else None
            else:
                documentation = RunnableDocumentation(
                    chain_name=final_chain_name,
                    prompt=prompt,
                    input_type=custom_input_type,
                    output_type=custom_output_type,
                    user_doc=user_doc,
                    sub_docs=(
                        RunnableBindingDocumentation(docs=sub_docs)
                        if len(sub_docs)
                        else None
                    ),
                )
        else:
            documentation = None

        super().__init__(
            bound=runnable,
            documentation=documentation,
            custom_input_type=custom_input_type,
            custom_output_type=custom_output_type,
            **kwargs,
        )


def render_io_doc(input, output) -> tuple[str]:
    if isinstance(input, ModelMetaclass):
        input_doc = render_model_doc(input, "Input")
    else:
        input_doc = f"### Input: {input.__name__}"

    if isinstance(output, ModelMetaclass):
        output_doc = render_model_doc(output, "Output")
    else:
        output_doc = f"### Output: {output.__name__}"

    return input_doc, output_doc


def render_model_doc(model: ModelMetaclass, input_or_output: str) -> str:
    field_info = get_field_info(model)

    tables = {
        cls: tabulate.tabulate(
            [
                (
                    field.name,
                    field.type,
                    field.required,
                    field.default,
                )
                for field in fields
            ],
            headers=["Name", "Type", "Required", "Default"],
            tablefmt="github",
        )
        for cls, fields in field_info.items()
    }

    return "\n".join(
        f"\n### {input_or_output}: {cls}\n\n{table}\n\n"
        for cls, table in tables.items()
    )


markdown_doc_template = """## {{ chain_name }}
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
{{ sub_docs }}
{% endif %}
"""

parallel_chains_template = """## These chains run in parallel
{% for doc in docs %}
<details markdown><summary>{{ doc.splitlines()[0].replace('#', '').strip() }}</summary>
{{ doc }}
</details>
{% endfor %}
"""

sequence_chains_template = """## These chains run in sequence
{% for doc in docs %}
<details markdown><summary>{{ doc.splitlines()[0].replace('#', '').strip() }}</summary>
{{ doc }}
</details>
{% endfor %}
"""

binding_chains_template = """## Sub-chain
{% for doc in docs %}
<details markdown><summary>{{ doc.splitlines()[0].replace('#', '').strip() }}</summary>
{{ doc }}
</details>
{% endfor %}
"""
