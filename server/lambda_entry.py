"""AWS entrypoints. Importing this module does not create local SQLite state."""
import json
import os

import boto3
from botocore.config import Config
from mangum import Mangum

from .app import create_app
from .auth import DemoAuth
from .cloud_store import DynamoStore
from .jobs import Jobs

_adapter = None


def handler(event, context):
    global _adapter
    if _adapter is None:
        store = DynamoStore()
        client = boto3.client('lambda', config=Config(connect_timeout=3, read_timeout=5,
            retries={'total_max_attempts': 1, 'mode': 'standard'}))

        def dispatch(job_id):
            client.invoke(FunctionName=os.environ['KIND_WORKER_NAME'], InvocationType='Event',
                Payload=json.dumps({'job_id': job_id}).encode())

        jobs = Jobs(store, dispatch, int(os.getenv('KIND_DAILY_AI_LIMIT', '20')))
        auth = DemoAuth(os.environ['KIND_ACCESS_DIGEST'], os.environ['KIND_SESSION_KEY'])
        app = create_app(store, auth=auth, public_host=os.environ['KIND_PUBLIC_HOST'], jobs=jobs)
        _adapter = Mangum(app, lifespan='off')
    return _adapter(event, context)


def worker(event, context):
    job_id = event.get('job_id')
    if not isinstance(job_id, str) or len(job_id) > 64:
        raise ValueError('Invalid job identifier')
    Jobs(DynamoStore(), None).work(job_id)
    return {'handled': True}
