from pathlib import Path

import nbformat
import pytest
from langchain_core.messages import AIMessage, ToolMessage


def validate_boundary(extra):
    nb = nbformat.read(Path(__file__).parents[1] / "ch05/01-subagent-delegation.ipynb", as_version=4)
    source = next(c.source for c in nb.cells if "parent-message-boundary" in c.metadata.get("tags", []))
    messages = [AIMessage(content="", tool_calls=[{"id": "task-1", "name": "task", "args": {"subagent_type": "researcher", "description": "research"}}]),
                ToolMessage(content="report ready", name="task", tool_call_id="task-1"), *extra]
    exec(source, {"first_result": {"messages": messages}, "AIMessage": AIMessage, "ToolMessage": ToolMessage})


def test_parent_has_only_delegation_result():
    validate_boundary([])


@pytest.mark.parametrize("extra", [
    [AIMessage(content="", tool_calls=[{"id": "read-1", "name": "read_file", "args": {"file_path": "/research/cache-choice.md"}}])],
    [ToolMessage(content="report content", name="read_file", tool_call_id="read-1")],
])
def test_parent_must_not_read_shared_file_before_observation(extra):
    with pytest.raises(AssertionError):
        validate_boundary(extra)
