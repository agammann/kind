from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
import pytest
from fastapi.testclient import TestClient
from .store import Store, WorkflowError, utcnow, iso
from .agent import prepare
from .app import create_app

@pytest.fixture
def store(tmp_path): return Store(str(tmp_path/'test.sqlite3'))

def pending(store,volunteer='v1',shift='s1'):
    inv=store.draft(shift,volunteer,'Please help if you are available.')
    return store.approve(inv['id'],inv['message'])

def test_real_persistence_and_full_workflow(store):
    result=prepare(store,'s1','rules')
    assert result['invitation']['status']=='draft'
    assert 'token' not in result['invitation']
    assert store.read()['shifts'][0]['assigned']==['v3']
    inv=store.approve(result['invitation']['id'],'Edited, approved message')
    assert store.public_invitation(inv['token'])['message']=='Edited, approved message'
    assert store.respond(inv['token'],'accepted')=={'status':'accepted'}
    assert Store(store.path).read()['shifts'][0]['assigned']==['v3','v1']

def test_qualification_optout_and_contact_cap(store):
    candidates=store.candidates('s1')
    assert [v['id'] for v in candidates['eligible']]==['v1','v2']
    for volunteer in ('v4','v5','v6','v3'):
        with pytest.raises(WorkflowError):store.draft('s1',volunteer,'Please help')

def test_approval_rechecks_availability(store):
    inv=store.draft('s1','v1','Hello')
    with store.transaction() as state: state['volunteers'][0]['availability']=[]
    with pytest.raises(WorkflowError):store.approve(inv['id'],'Hello')

def test_decline_gets_next_candidate(store):
    inv=pending(store)
    store.respond(inv['token'],'declined')
    assert prepare(store,'s1','rules')['invitation']['volunteer_id']=='v2'
    assert store.read()['shifts'][0]['assigned']==['v3']

def test_concurrent_acceptance_never_overfills(store):
    a,b=pending(store,'v1'),pending(store,'v2')
    def accept(inv):
        try:return store.respond(inv['token'],'accepted')['status']
        except WorkflowError:return 'closed'
    with ThreadPoolExecutor(2) as pool: results=list(pool.map(accept,[a,b]))
    assert sorted(results)==['accepted','closed']
    assert len(store.read()['shifts'][0]['assigned'])==2

def test_repeated_approval_and_acceptance_are_idempotent(store):
    inv=pending(store)
    assert store.approve(inv['id'],'different')['token']==inv['token']
    store.respond(inv['token'],'accepted')
    store.respond(inv['token'],'accepted')
    assert len(store.read()['shifts'][0]['assigned'])==2

def test_acceptance_rechecks_conflicting_commitments(store):
    inv=pending(store)
    with store.transaction() as state:
        state['shifts'][1].update(start=state['shifts'][0]['start'],end=state['shifts'][0]['end'],assigned=['v1'])
    with pytest.raises(WorkflowError):store.respond(inv['token'],'accepted')

def test_expired_invitation_cannot_assign(store):
    inv=pending(store)
    with store.transaction() as state: state['invitations'][0]['expires_at']=iso(utcnow()-timedelta(minutes=1))
    assert store.public_invitation(inv['token'])['status']=='expired'
    with pytest.raises(WorkflowError):store.respond(inv['token'],'accepted')

def test_cancelled_invitation_is_revoked(store):
    inv=pending(store)
    store.cancel_invitation(inv['id'])
    with pytest.raises(WorkflowError):store.respond(inv['token'],'accepted')

def test_cancellation_reopens_gap_without_reinviting_cancelled_person(store):
    store.cancel_assignment('s3','v2')
    assert store.scan()['open_shifts']==3
    assert 'v2' not in [v['id'] for v in store.candidates('s3')['eligible']]

def test_api_coordinator_boundary_and_public_response(store):
    app=create_app(store)
    with TestClient(app) as owner,TestClient(app) as volunteer:
        assert volunteer.get('/api/workspace').status_code==401
        assert owner.post('/api/session').status_code==200
        result=owner.post('/api/shifts/s1/prepare',json={'mode':'rules'}).json()
        inv_id=result['invitation']['id']
        assert volunteer.post(f'/api/invitations/{inv_id}/approve',json={'message':'Hi'}).status_code==401
        inv=owner.post(f'/api/invitations/{inv_id}/approve',json={'message':'Hi'}).json()
        public=volunteer.get('/api/volunteer/'+inv['token']).json()
        assert 'volunteers' not in public and 'assigned' not in public['shift']
        assert volunteer.post('/api/volunteer/'+inv['token']+'/respond',json={'decision':'accepted'}).status_code==200
        assert owner.get('/api/workspace').json()['shifts'][0]['assigned']==['v3','v1']

def test_cross_site_requests_and_untrusted_hosts_blocked(store):
    with TestClient(create_app(store)) as client:
        assert client.post('/api/session',headers={'Origin':'https://attacker.example'}).status_code==403
        assert client.post('/api/session',headers={'sec-fetch-site':'cross-site'}).status_code==403
        assert client.post('/api/session',headers={'Host':'attacker.example'}).status_code==400

def test_gap_scan_is_not_spammy(store):
    store.scan();before=len(store.read()['activity']);store.scan()
    assert len(store.read()['activity'])==before

def test_live_mode_is_not_faked(store,monkeypatch):
    monkeypatch.delenv('KIND_BEDROCK_MODEL_ID',raising=False)
    with pytest.raises(WorkflowError,match='Live Strands needs'):
        prepare(store,'s1','bedrock')
    assert store.read()['invitations']==[]
