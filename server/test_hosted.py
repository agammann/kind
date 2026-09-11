import hashlib
import time
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient

from .agent import prepare
from .app import create_app
from .auth import DemoAuth
from .jobs import Jobs
from .store import Store, WorkflowError
from .test_workflow import store


def auth():
    return DemoAuth(hashlib.sha256(b'fictional-test-access-code').hexdigest(), 'test-signing-key-for-tests-only-12345678901234567890')


def test_hosted_requires_login_and_sessions_survive_app_restart(store):
    app=create_app(store,auth=auth(),public_host='demo.example')
    with TestClient(app,base_url='https://demo.example') as client:
        assert client.post('/api/session',json={}).status_code==401
        assert client.post('/api/session',json={'access_code':'wrong'}).status_code==401
        assert client.get('/api/workspace').status_code==401
        login=client.post('/api/session',json={'access_code':'fictional-test-access-code'})
        assert login.status_code==200
        assert 'Secure' in login.headers['set-cookie'] and 'HttpOnly' in login.headers['set-cookie']
        assert client.get('/api/workspace').json()['hosted'] is True
        assert client.post('/api/session',headers={'Origin':'https://evil.example'},json={}).status_code==403
        cookie=client.cookies.get('kind_coordinator')
        with TestClient(create_app(store,auth=auth(),public_host='demo.example'),base_url='https://demo.example') as fresh:
            fresh.cookies.set('kind_coordinator',cookie)
            assert fresh.get('/api/workspace').status_code==200
        client.post('/api/logout')
        assert client.get('/api/workspace').status_code==401


def test_signed_cookie_rejects_tampering_expiry_and_wrong_key(monkeypatch):
    signer=auth()
    token=signer.issue()
    assert signer.valid(token)
    assert not signer.valid(token+'x')
    assert not signer.valid('missing.parts')
    other=DemoAuth(signer.access_digest,'different-signing-key-123456789012345678901234567890')
    assert not other.valid(token)
    monkeypatch.setattr(time,'time',lambda:int(token.split('.')[0])+1)
    assert not signer.valid(token)


def test_jobs_reserve_budget_run_once_and_preserve_approval_boundary(store):
    dispatched=[]
    jobs=Jobs(store,dispatched.append,daily_limit=1)
    job_id=jobs.start('s1')['job_id']
    assert dispatched==[job_id]
    with pytest.raises(WorkflowError):jobs.start('s2')
    calls=[]
    def runner(workspace,shift,mode):
        calls.append(mode)
        return prepare(workspace,shift,'rules')
    jobs.work(job_id,runner)
    jobs.work(job_id,runner)
    assert calls==['bedrock']
    result=jobs.get(job_id)
    assert result['status']=='complete'
    assert result['result']['invitation']['status']=='draft'
    assert 'token' not in result['result']['invitation']
    assert store.read()['shifts'][0]['assigned']==['v3']
    with pytest.raises(WorkflowError,match='limit'):jobs.start('s2')


def test_job_failure_and_expiration_are_visible(store):
    jobs=Jobs(store,lambda _:None)
    job_id=jobs.start('s1')['job_id']
    def fail(*args):raise RuntimeError('sensitive provider detail')
    jobs.work(job_id,fail)
    assert jobs.get(job_id)['status']=='failed'
    assert 'sensitive' not in str(jobs.get(job_id))
    job_id=jobs.start('s1')['job_id']
    with store.transaction() as state:state['_job']['expires']=int(time.time())-1
    jobs.work(job_id,fail)
    assert jobs.get(job_id)['status']=='failed'
    assert store.read()['invitations']==[]


def test_job_routes_and_internal_state_require_coordinator(store):
    jobs=Jobs(store,lambda _:None)
    app=create_app(store,jobs=jobs)
    with TestClient(app) as client:
        assert client.post('/api/shifts/s1/prepare',json={'mode':'bedrock'}).status_code==401
        assert client.get('/api/jobs/unknown').status_code==401
        client.post('/api/session')
        response=client.post('/api/shifts/s1/prepare',json={'mode':'bedrock'})
        assert response.status_code==202
        assert client.get('/api/jobs/'+response.json()['job_id']).json()['status']=='pending'
        state=client.get('/api/workspace').json()
        assert '_job' not in state and '_usage' not in state


def test_dynamodb_rejects_stale_snapshot(store):
    if isinstance(store,Store) and hasattr(store,'path'):
        pytest.skip('Conditional version writes are specific to DynamoDB.')
    with pytest.raises(WorkflowError,match='roster changed'):
        with store.transaction() as older:
            with store.transaction() as newer:newer['organization']='New name'
            older['organization']='Stale name'
    assert store.read()['organization']=='New name'
