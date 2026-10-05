from pathlib import Path

import nbformat
import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage


def run_validation(messages):
    path = Path(__file__).parents[1] / "ch01/01-agent-harness.ipynb"
    nb = nbformat.read(path, as_version=4)
    cell = next(c for c in nb.cells if "echo-validation" in c.metadata.get("tags", []))
    exec(cell.source, {"lc_result": {"messages": messages}, "ECHO_TEXT": "hello deepagents"})


def exchange(*, text="hello deepagents", status="success", name="echo", call_id="echo-1"):
    return [HumanMessage(content="echo"),
            AIMessage(content="", tool_calls=[{"id": "echo-1", "name": "echo", "args": {"text": text}}]),
            ToolMessage(content=f"echo: {text}" if status == "success" else "text: Field required", name=name, tool_call_id=call_id, status=status),
            AIMessage(content="done")]


def test_accepts_successful_echo():
    run_validation(exchange())


@pytest.mark.parametrize("messages", [
    [HumanMessage(content="echo"), AIMessage(content="I did it")],
    exchange(status="error"),
    exchange(text="wrong text"),
    exchange(name="different_tool"),
    exchange(call_id="unrelated-id"),
])
def test_rejects_unfulfilled_echo(messages):
    with pytest.raises(AssertionError):
        run_validation(messages)
