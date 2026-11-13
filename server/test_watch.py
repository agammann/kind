from threading import Event

import pytest
from fastapi.testclient import TestClient

from . import app as app_module
from .store import ConcurrentWrite, WorkflowError


def test_watch_continues_after_conditional_write_conflict(monkeypatch):
    class ConflictingOnce:
        def __init__(self):
            self.calls = 0
            self.completed = Event()

        def scan(self):
            self.calls += 1
            if self.calls == 1:
                raise ConcurrentWrite('version conflict')
            self.completed.set()

    store = ConflictingOnce()
    monkeypatch.setattr(app_module, 'SCAN_INTERVAL_SECONDS', 0.01)
    with TestClient(app_module.create_app(store)):
        assert store.completed.wait(5), 'watcher did not retry after contention'
    assert store.calls >= 2


def test_watch_does_not_hide_other_workflow_errors():
    class Failing:
        def __init__(self):
            self.called = Event()

        def scan(self):
            self.called.set()
            raise WorkflowError('unexpected failure')

    store = Failing()
    with pytest.raises(WorkflowError, match='unexpected failure'):
        with TestClient(app_module.create_app(store)):
            assert store.called.wait(5), 'watcher did not start'
