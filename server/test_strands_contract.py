"""Exercise the real agent loop with a deterministic, offline model."""
import json

from strands.models import Model

from .agent import prepare
from .store import Store, WorkflowError


class ScriptedModel(Model):
    def __init__(self, actions):
        self.actions=iter(actions)
        self.calls=0

    def get_config(self): return {'context_window_limit': 100000}
    def update_config(self, **kwargs): pass

    async def structured_output(self, *args, **kwargs):
        raise NotImplementedError
        yield

    async def stream(self, messages, tool_specs=None, system_prompt=None, **kwargs):
        self.calls+=1
        action=next(self.actions)
        if isinstance(action,Exception): raise action
        yield {'messageStart': {'role': 'assistant'}}
        if isinstance(action, str):
            yield {'contentBlockStart': {'start': {}}}
            yield {'contentBlockDelta': {'delta': {'text': action}}}
            yield {'contentBlockStop': {}}
            yield {'messageStop': {'stopReason': 'end_turn'}}
        else:
            name, payload=action
            yield {'contentBlockStart': {'start': {'toolUse': {'name': name, 'toolUseId': str(self.calls)}}}}
            yield {'contentBlockDelta': {'delta': {'toolUse': {'input': json.dumps(payload)}}}}
            yield {'contentBlockStop': {}}
            yield {'messageStop': {'stopReason': 'tool_use'}}


def test_real_agent_stages_only_an_eligible_draft(tmp_path):
    store=Store(str(tmp_path/'agent.sqlite3'))
    model=ScriptedModel([('get_shift_context', {}), ('check_eligibility', {}),
        ('prepare_invitation', {'volunteer_id': 'v1'}), 'Invented shift details'])
    result=prepare(store, 's1', 'bedrock', model=model)
    assert model.calls==4
    assert [item['tool'] for item in result['trace']]==['get_shift_context','check_eligibility','prepare_invitation']
    assert result['invitation']['status']=='draft' and result['invitation']['volunteer_id']=='v1'
    assert 'token' not in result['invitation'] and 'Invented shift details' not in result['summary']
    assert store.read()['shifts'][0]['assigned']==['v3']


def test_real_agent_rejects_early_and_ineligible_drafts(tmp_path):
    store=Store(str(tmp_path/'denied.sqlite3'))
    model=ScriptedModel([('prepare_invitation', {'volunteer_id':'v1'}),
        ('get_shift_context', {}), ('check_eligibility', {}),
        ('prepare_invitation', {'volunteer_id':'v4'}), 'Finished'])
    try:
        prepare(store, 's1', 'bedrock', model=model)
    except WorkflowError as exc:
        assert 'did not prepare a draft' in exc.message
    else:
        raise AssertionError('An ineligible draft should not be created')
    assert model.calls==5
    assert not store.read()['invitations']


def test_real_agent_enforces_five_model_call_limit(tmp_path):
    store=Store(str(tmp_path/'budget.sqlite3'))
    model=ScriptedModel([('get_shift_context', {})]*6)
    try:
        prepare(store, 's1', 'bedrock', model=model)
    except WorkflowError as exc:
        assert exc.status==503 and 'five-step limit' in exc.message
    else:
        raise AssertionError('The sixth model call should be blocked')
    assert model.calls==5
    assert not store.read()['invitations']


def test_provider_failures_remain_sanitized(tmp_path):
    store=Store(str(tmp_path/'error.sqlite3'))
    model=ScriptedModel([RuntimeError('sensitive provider detail')])
    try:
        prepare(store, 's1', 'bedrock', model=model)
    except WorkflowError as exc:
        assert exc.status==503 and 'could not complete' in exc.message
        assert 'sensitive provider detail' not in exc.message
    else:
        raise AssertionError('A provider failure should be rejected')
    assert model.calls==1 and not store.read()['invitations']
