"""A complete two-round planning case, checked through real tools and artifacts."""
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
    cells = {c.id: c.source for c in nbformat.read(NOTEBOOK, as_version=4).cells}
    ns = {}
    for key in ('ch04-imports', 'ch04-case-data', 'ch04-case-tools'):
        exec(cells[key], ns)
    for key in ('ch04-case-agent', 'ch04-first-run', 'ch04-todo-evidence',
                'ch04-case-check', 'ch04-controlled-case'):
        tree = ast.parse(cells[key])
        module = ast.Module(body=[node for node in tree.body if isinstance(node, ast.FunctionDef)], type_ignores=[])
        exec(compile(module, str(NOTEBOOK), 'exec'), ns)
    return ns


@pytest.mark.parametrize('plan', [
    None, [],
    [{'content': 'A different plan', 'status': 'pending'}],
    [{'content': 'Continue manual review', 'status': 'in_progress'}],
    [{'content': 'Checked', 'status': 'completed'}, {'content': 'Follow-up', 'status': 'pending'}],
])
def test_valid_artifacts_do_not_require_fixed_todo_content_or_lifecycle(experiment, plan):
    state, ctx = experiment['run_controlled_case'](plan=plan)
    experiment['check_case_result'](state, ctx)


@pytest.mark.parametrize('options', [
    {'include_search': False}, {'missing_dimension': True}, {'empty_results': True},
])
def test_completed_does_not_override_missing_artifacts(experiment, options):
    plan = experiment['plan_items'](['Research'], 'completed')
    state, ctx = experiment['run_controlled_case'](plan=plan, **options)
    assert state['todos'] == plan
    with pytest.raises(AssertionError):
        experiment['check_case_result'](state, ctx)


@pytest.mark.parametrize('defect', ['call-id', 'tool-name', 'error-status', 'query', 'execution-record', 'submission-record'])
def test_tool_evidence_must_match_actual_requests_and_records(experiment, defect):
    state, ctx = experiment['run_controlled_case']()
    reply = next(m for m in state['messages'] if isinstance(m, ToolMessage) and m.name == 'internet_search')
    if defect == 'call-id':
        reply.tool_call_id = 'unrelated'
    elif defect == 'tool-name':
        reply.name = 'unrelated'
    elif defect == 'error-status':
        reply.status = 'error'
    elif defect == 'query':
        call = next(c for m in state['messages'] if isinstance(m, AIMessage)
                    for c in m.tool_calls if c['id'] == reply.tool_call_id)
        call['args']['query'] = 'unrelated query'
    elif defect == 'execution-record':
        ctx['searches'][0]['results'] = []
    else:
        ctx['submissions'][-1]['report']['conclusion'] = 'Changed after submission'
    with pytest.raises(AssertionError):
        experiment['check_case_result'](state, ctx)


@pytest.mark.parametrize('defect', ['framework', 'dimension', 'source', 'conclusion', 'freshness'])
def test_report_contract_requires_coverage_and_observed_sources(experiment, defect):
    _, ctx = experiment['run_controlled_case']()
    report = deepcopy(ctx['submissions'][-1]['report'])
    rows = report['comparisons']
    if defect == 'framework':
        rows.pop('Codex SDK')
    elif defect == 'dimension':
        rows['Codex SDK'].pop('integration')
    elif defect == 'source':
        rows['Codex SDK']['sources'] = ['https://invented.example/source']
    elif defect == 'conclusion':
        report['conclusion'] = ''
    else:
        for search in ctx['searches']:
            search['stage'] = 'initial'
    assert experiment['assess_report'](report, ctx['searches'], experiment['FINAL_DIMENSIONS'], require_fresh=True)


@pytest.mark.parametrize('plan', [
    [{'content': 'task', 'status': 'done'}], [{'content': '', 'status': 'pending'}],
])
def test_invalid_todo_structure_is_rejected(experiment, plan):
    state, _ = experiment['run_controlled_case']()
    state['todos'] = plan  # Deliberately corrupt an actual run to test the validator.
    with pytest.raises(AssertionError):
        experiment['check_todo_state'](state)


def test_final_todo_must_match_last_successful_write(experiment):
    state, _ = experiment['run_controlled_case'](plan=experiment['plan_items'](['Review']))
    state['todos'] = experiment['plan_items'](['Different state'])
    with pytest.raises(AssertionError, match='最后一次'):
        experiment['check_todo_state'](state)


def test_successful_todo_requires_matching_request(experiment):
    state, _ = experiment['run_controlled_case'](plan=experiment['plan_items'](['Review']))
    reply = next(m for m in state['messages'] if isinstance(m, ToolMessage) and m.name == 'write_todos')
    reply.tool_call_id = 'unrelated'
    with pytest.raises(AssertionError, match='对应'):
        experiment['successful_todo_updates'](state)


@pytest.mark.parametrize('use_todos', [True, False])
def test_complete_case_revises_draft_after_feedback_in_same_thread(experiment, use_todos):
    ns = experiment
    scripted = ns['scripted_case']()
    if not use_todos:
        scripted.responses = [m for m in scripted.responses
                              if not any(c['name'] == 'write_todos' for c in m.tool_calls)]
    ctx = ns['new_context']()
    agent = ns['create_deep_agent'](model=scripted, tools=ns['make_case_tools'](ctx, local_only=True),
                                   middleware=[ns['TodoListMiddleware']()], checkpointer=ns['InMemorySaver']())
    config = {'configurable': {'thread_id': 'test-case'}, 'recursion_limit': 60}
    first, _ = ns['run_case_turn'](agent, ns['FIRST_REQUEST'], config)
    assert not ctx['submissions'][-1]['issues']
    ns['check_case_result'](first, ctx, expanded=False)
    assert not agent.get_state({'configurable': {'thread_id': 'another-thread'}}).values
    ctx['stage'] = 'expanded'
    final, _ = ns['run_case_turn'](agent, ns['FOLLOWUP_REQUEST'], config)
    assert ctx['reviews'] and ctx['reviews'][0]['issues']
    assert any('integration' in issue for issue in ctx['reviews'][0]['issues'])
    assert all(not item['issues'] for item in ctx['submissions'])
    assert {search['stage'] for search in ctx['searches']} == {'initial', 'expanded'}
    ns['check_case_result'](final, ctx)
    if not use_todos:
        assert not ns['successful_todo_updates'](final)
