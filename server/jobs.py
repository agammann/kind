"""Persisted AI jobs. Only an authenticated coordinator can enqueue a job."""
import secrets
import time
from datetime import datetime, timezone

from .agent import prepare
from .store import WorkflowError


class Jobs:
    def __init__(self, store, dispatch, daily_limit=20):
        self.store, self.dispatch, self.daily_limit = store, dispatch, daily_limit

    def start(self, shift_id):
        now = int(time.time())
        day = datetime.now(timezone.utc).date().isoformat()
        job = {'id': secrets.token_urlsafe(18), 'shift_id': shift_id, 'status': 'pending', 'expires': now + 400}
        with self.store.transaction() as state:
            shift = self.store.find(state, 'shifts', shift_id)
            if len(shift['assigned']) >= shift['required']:
                raise WorkflowError('This shift is already covered.')
            previous = state.get('_job', {})
            if previous.get('status') in ('pending', 'running') and previous['expires'] > now:
                raise WorkflowError('An invitation is already being prepared. Please wait.')
            usage = state.get('_usage', {'day': day, 'count': 0})
            if usage['day'] != day:
                usage = {'day': day, 'count': 0}
            if usage['count'] >= self.daily_limit:
                raise WorkflowError('Today’s live AI demo limit has been reached. Rules mode is still available.', 429)
            usage['count'] += 1
            state['_usage'], state['_job'] = usage, job
        try:
            self.dispatch(job['id'])
        except Exception as exc:
            self.finish(job['id'], error='The worker could not be started. Please try again later.')
            raise WorkflowError('The worker could not be started. Please try again later.', 503) from exc
        return {'job_id': job['id'], 'status': 'pending'}

    def get(self, job_id):
        job = self.store.read().get('_job', {})
        if job.get('id') != job_id:
            raise WorkflowError('This preparation job is no longer available. Check the invitation list.', 404)
        if job['status'] in ('pending', 'running') and job['expires'] <= time.time():
            return {'status': 'failed', 'error': 'The worker did not finish in time. Check saved drafts before trying again.'}
        return {k: v for k, v in job.items() if k in ('status', 'result', 'error')}

    def finish(self, job_id, result=None, error=None):
        # A concurrent roster write can briefly conflict with saving job status.
        for attempt in range(3):
            try:
                with self.store.transaction() as state:
                    job = state.get('_job', {})
                    if job.get('id') != job_id:
                        return
                    job.update(status='failed' if error else 'complete')
                    job['error' if error else 'result'] = error or result
                return
            except WorkflowError:
                if attempt == 2:
                    raise

    def work(self, job_id, runner=prepare):
        with self.store.transaction() as state:
            job = state.get('_job', {})
            if job.get('id') != job_id or job.get('status') != 'pending' or job['expires'] <= time.time():
                return
            job['status'] = 'running'
            shift_id = job['shift_id']
        try:
            result = runner(self.store, shift_id, 'bedrock')
        except Exception:
            self.finish(job_id, error='Live AI could not finish. Check saved drafts before retrying. No invitation was approved or sent.')
        else:
            self.finish(job_id, result=result)
