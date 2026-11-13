import time
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

from .app import create_app
from .store import WorkflowError, utcnow, iso, parse
from .test_workflow import store, pending, track_initial_scan


def test_restart_revokes_links_refreshes_dates_and_preserves_budget(store):
    invitation=pending(store)
    with store.transaction() as state:
        state['_usage']={'day':'2099-01-01','count':20}
        state['_job']={'id':'old','status':'complete'}
        for shift in state['shifts']:
            shift['start']=iso(utcnow()-timedelta(days=2))
            shift['end']=iso(utcnow()-timedelta(days=1))
    store.restart_sample()
    state=store.read()
    assert state['_usage']=={'day':'2099-01-01','count':20}
    assert '_job' not in state
    assert all(parse(s['start'])>utcnow() for s in state['shifts'])
    assert store.candidates('s1')['eligible']
    assert state['invitations']==[]
    with pytest.raises(WorkflowError): store.public_invitation(invitation['token'])


def test_restart_rejects_active_job_and_non_sample(store):
    with store.transaction() as state:
        state['_job']={'id':'active','status':'running','expires':time.time()+300}
    previous=store.read()
    with pytest.raises(WorkflowError,match='preparation'):store.restart_sample()
    assert store.read()==previous
    with store.transaction() as state:
        state['_job']['status']='complete'
        state['sample_data']=False
    with pytest.raises(WorkflowError,match='fictional'):store.restart_sample()


def test_restart_requires_session_explicit_body_and_same_origin(store, monkeypatch):
    scan_done, scan_errors=track_initial_scan(store, monkeypatch)
    with TestClient(create_app(store)) as client:
        assert scan_done.wait(5) and not scan_errors
        assert client.post('/api/sample/restart',json={'confirm':'restart fictional sample'}).status_code==401
        client.post('/api/session')
        assert client.post('/api/sample/restart',json={}).status_code==422
        assert client.post('/api/sample/restart',json={'confirm':'restart fictional sample'},headers={'Origin':'https://evil.example'}).status_code==403
        response=client.post('/api/sample/restart',json={'confirm':'restart fictional sample'})
        assert response.status_code==200, response.text
