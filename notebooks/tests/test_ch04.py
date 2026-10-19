"""Check chapter 4 against real controlled tool runs, including false completion claims."""
import ast
from copy import deepcopy
from pathlib import Path

import nbformat
import pytest
from langchain_core.messages import AIMessage, ToolMessage

NOTEBOOK = Path(__file__).parents[1] / 'ch04/01-task-planning.ipynb'


@pytest.fixture
def experiment(monkeypatch):
    monkeypatch.setenv('COURSE_MODE', 'offline')
    nb = nbformat.read(NOTEBOOK, as_version=4)
    cells = {cell.id: cell.source for cell in nb.cells}
    namespace = {'MODE': 'offline', 'deepcopy': deepcopy}
    for cell_id in ('ch04-imports', 'ch04-search', 'ch04-research-agent',
                    'ch04-research-check', 'ch04-controlled-research'):
        exec(cells[cell_id], namespace)
    tree = ast.parse(cells['ch04-todo-evidence'])
    definitions = ast.Module(body=[node for node in tree.body if isinstance(node, ast.FunctionDef)], type_ignores=[])
    exec(compile(definitions, str(NOTEBOOK), 'exec'), namespace)
    return namespace


@pytest.mark.parametrize('plan', [
    None,
    [],
    [{'content': 'Different task wording', 'status': 'pending'}],
    [{'content': 'Review evidence', 'status': 'in_progress'}],
    [{'content': 'Checked evidence', 'status': 'completed'},
     {'content': 'Follow-up review', 'status': 'pending'}],
])
def test_research_accepts_optional_and_varied_plans(experiment, plan):
    state, log = experiment['run_controlled_research'](plan=plan)
    experiment['check_research'](state, log)


@pytest.mark.parametrize('options', [
    {'run_searches': False},
    {'empty_results': True},
    {'report': 'All tasks are completed.'},
    {'report': ''},
    {'report': 'https://invented.example/one\nhttps://invented.example/two'},
])
def test_completed_claim_does_not_override_missing_artifacts(experiment, options):
    completed = experiment['todos'](['completed'] * 3)
    state, log = experiment['run_controlled_research'](plan=completed, **options)
    assert state['todos'] == completed
    with pytest.raises(AssertionError):
        experiment['check_research'](state, log)


@pytest.mark.parametrize('defect', ['call-id', 'tool-name', 'error-status', 'query', 'execution-log', 'extra-source'])
def test_research_rejects_unrelated_or_inconsistent_evidence(experiment, defect):
    state, log = experiment['run_controlled_research']()
    reply = next(m for m in state['messages'] if isinstance(m, ToolMessage) and m.name == 'internet_search')
    if defect == 'call-id':
        reply.tool_call_id = 'unrelated'
    elif defect == 'tool-name':
        reply.name = 'other-tool'
    elif defect == 'error-status':
        reply.status = 'error'
    elif defect == 'query':
        call = next(c for m in state['messages'] if isinstance(m, AIMessage)
                    for c in m.tool_calls if c['id'] == reply.tool_call_id)
        call['args']['query'] = 'unrelated query'
    elif defect == 'execution-log':
        log[0]['results'] = 0
    else:
        state['messages'][-1].content += '\nhttps://invented.example/source'
    with pytest.raises(AssertionError):
        experiment['check_research'](state, log)


@pytest.mark.parametrize('plan', [
    [{'content': 'task', 'status': 'done'}],
    [{'content': '', 'status': 'pending'}],
])
def test_invalid_todo_structure_is_rejected(experiment, plan):
    state, log = experiment['run_controlled_research']()
    state['todos'] = plan  # Deliberately corrupt an actual run for validator regression checks.
    with pytest.raises(AssertionError):
        experiment['check_research'](state, log)


def test_last_successful_todo_must_match_state(experiment):
    state, log = experiment['run_controlled_research'](
        plan=[{'content': 'Evidence review', 'status': 'pending'}],
    )
    state['todos'] = [{'content': 'Different state', 'status': 'pending'}]
    with pytest.raises(AssertionError, match='最后一次'):
        experiment['check_research'](state, log)


def test_successful_todo_requires_matching_request(experiment):
    state, _ = experiment['run_controlled_research'](
        plan=[{'content': 'Evidence review', 'status': 'pending'}],
    )
    reply = next(m for m in state['messages'] if isinstance(m, ToolMessage) and m.name == 'write_todos')
    reply.tool_call_id = 'unrelated'
    with pytest.raises(AssertionError, match='对应'):
        experiment['successful_todo_updates'](state)
