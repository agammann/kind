"""Exercise a packaged artifact inside the official Lambda Python container."""
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import zipfile


def main():
    package=Path(sys.argv[1])
    target=Path(tempfile.mkdtemp(prefix='kind-smoke-'))
    with zipfile.ZipFile(package) as archive:archive.extractall(target)
    sys.path.insert(0,str(target))
    os.environ['KIND_HOSTED']='1'
    os.environ['AWS_EC2_METADATA_DISABLED']='true'
    from server import lambda_entry
    from server.app import create_app
    from server.auth import DemoAuth
    from server.store import Store
    from server.agent import prepare
    from mangum import Mangum
    store=Store(str(target/'smoke.sqlite3'))
    invitation=prepare(store,'s1','rules')['invitation']
    assert invitation['status']=='draft' and 'token' not in invitation
    auth=DemoAuth(hashlib.sha256(b'smoke-code').hexdigest(),'smoke-signing-key-123456789012345678901234567890')
    adapter=Mangum(create_app(store,auth=auth,public_host='demo.example'),lifespan='off')
    def request(path,method='GET',body=None,cookies=None):
        event={'version':'2.0','routeKey':'$default','rawPath':path,'rawQueryString':'',
            'headers':{'host':'demo.example','content-type':'application/json','x-forwarded-proto':'https'},
            'requestContext':{'stage':'$default','domainName':'demo.example','http':{'method':method,'path':path,'sourceIp':'127.0.0.1','protocol':'HTTP/1.1'}},
            'body':json.dumps(body) if body is not None else None,'isBase64Encoded':False,'cookies':cookies or []}
        return adapter(event,SimpleNamespace(aws_request_id='local-smoke'))
    assert request('/api/workspace')['statusCode']==401
    login=request('/api/session','POST',{'access_code':'smoke-code'})
    assert login['statusCode']==200
    cookie=login['cookies'][0].split(';')[0]
    state=request('/api/workspace',cookies=[cookie])
    assert state['statusCode']==200 and json.loads(state['body'])['hosted']
    assert request('/')['statusCode']==200
    print('Linux Lambda package passed: imports, rules draft, authentication, API v2 adapter, persisted roster and frontend. No AWS API calls made.')


if __name__=='__main__':
    main()
