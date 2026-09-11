import pytest
from .agent import default_message, prepare
from .test_workflow import store


@pytest.mark.parametrize('start,end,expected',[
    ('2026-09-13T16:00:00+00:00','2026-09-13T18:00:00+00:00','09:00 AM to 11:00 AM PDT'),
    ('2026-12-13T16:00:00+00:00','2026-12-13T18:00:00+00:00','08:00 AM to 10:00 AM PST'),
])
def test_invitation_uses_local_clock_and_dst(start,end,expected):
    shift={'start':start,'end':end,'title':'Pantry preparation','location':'Riverbend'}
    assert expected in default_message(shift,'Maya Chen','America/Los_Angeles')


def test_agent_draft_uses_authoritative_shift_not_model_prose(store,monkeypatch):
    import strands
    class AgentStub:
        def __init__(self,**kwargs): self.tools=kwargs['tools']
        def __call__(self,prompt):
            self.tools[0]()
            self.tools[1]()
            self.tools[2](volunteer_id='v1')
            return 'Invented model prose: 4 PM at an unrelated location.'
    monkeypatch.setattr(strands,'Agent',AgentStub)
    result=prepare(store,'s1','bedrock',model=object())
    assert '09:00 AM' in result['invitation']['message']
    assert 'Riverbend Community Pantry' in result['invitation']['message']
    assert 'Invented model prose' not in result['summary']
    assert result['invitation']['status']=='draft'
