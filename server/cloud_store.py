"""DynamoDB persistence with conditional writes across Lambda instances."""
import json
import os
import threading
from contextlib import contextmanager

import boto3
from boto3.dynamodb.conditions import Attr
from botocore.config import Config

from .store import Store, WorkflowError, seed_state


class DynamoStore(Store):
    def __init__(self, table_name=None):
        self.table_name = table_name or os.environ['KIND_TABLE_NAME']
        self.local = threading.local()

    @property
    def table(self):
        # boto3 resources are not shared across FastAPI worker threads.
        if not hasattr(self.local, 'table'):
            resource = boto3.Session().resource('dynamodb', region_name=os.getenv('AWS_REGION', 'us-west-2'),
                config=Config(connect_timeout=3, read_timeout=5, retries={'total_max_attempts': 2, 'mode': 'standard'}))
            self.local.table = resource.Table(self.table_name)
        return self.local.table

    def item(self):
        found = self.table.get_item(Key={'pk': 'workspace'}, ConsistentRead=True).get('Item')
        if found:
            return found
        seeded = {'pk': 'workspace', 'version': 1, 'document': json.dumps(seed_state())}
        try:
            self.table.put_item(Item=seeded, ConditionExpression=Attr('pk').not_exists())
            return seeded
        except self.table.meta.client.exceptions.ConditionalCheckFailedException:
            return self.table.get_item(Key={'pk': 'workspace'}, ConsistentRead=True)['Item']

    def read(self):
        return json.loads(self.item()['document'])

    @contextmanager
    def transaction(self):
        item = self.item()
        state = json.loads(item['document'])
        yield state
        document = json.dumps(state)
        if document == item['document']:
            return
        if len(document.encode()) > 350000:
            raise WorkflowError('This sample workspace is full. Export or reset it before adding more history.', 409)
        try:
            self.table.put_item(Item={'pk': 'workspace', 'version': item['version'] + 1, 'document': document},
                ConditionExpression=Attr('version').eq(item['version']))
        except self.table.meta.client.exceptions.ConditionalCheckFailedException as exc:
            raise WorkflowError('The roster changed during this action. Refresh and try again.', 409) from exc
